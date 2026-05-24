from __future__ import annotations

from math import pi, atan2, asin

import numpy as np

import gmatpyplus as gp
from basics import GmatObject


class FieldOfView(GmatObject):
    def __init__(self, attached_object: gp.Imager | gp.Antenna, fov_type: str = None, name: str = 'DefaultFOV'):
        allowed_fov_types = ['ConicalFOV', 'CustomFOV', 'RectangularFOV', None]
        if fov_type not in allowed_fov_types:
            raise TypeError(f'FieldOfView type given in fov_type "{fov_type}" is not recognized. Must be one of:\n'
                            f'{allowed_fov_types}')
        if fov_type is None:
            self.fov_type = 'RectangularFOV'
        else:
            self.fov_type = fov_type

        super().__init__(self.fov_type, name)

        self.attached_obj = attached_object  # e.g. an Imager or Antenna that uses this FieldOfView

        # gmat.Construct returns a GmatBase for FOV, so get object in FOV type from Validator
        # self.gmat_obj = gp.Moderator().gmat_obj.FindObject(self.name)
        # self.gmat_obj = gp.Moderator().gmat_obj.CreateFieldOfView(self.fov_type, self.name)
        # self.gmat_obj = gp.Validator().FindObject(self.name)
        # self.gmat_obj = gmat.Construct('RectangularFOV', 'DefRectFOV')
        # self.gmat_obj = gp.Moderator().gmat_obj.GetFieldOfView(self.name)
        # print(type(self.gmat_obj))
        # print(self.gmat_obj)
        #
        # self.gmat_obj.Help()

        # # TODO remove (method checking only)
        # self.CheckTargetVisibility([0, 0, 0])
        # pass

    # def CheckTargetVisibility(self, target: list[int | float]):
    #     rv3 = gmat.Rvector3(target)  # convert to a GMAT Rvector3 object
    #     return self.gmat_obj.CheckTargetVisibility(rv3)

    @staticmethod
    def RADECtoConeClock(RA, dec):
        # FIXME: source code assigns both lines below to clock, so unsure which should be cone (see GMT-8120)
        cone = pi / 2 - dec
        clock = RA
        return cone, clock

    @staticmethod
    def UnitVecToRADEC(unit_vec: np.ndarray):
        if unit_vec[0] == 0 and unit_vec[1] == 0:
            if unit_vec[2] > 0:
                dec = pi / 2
            elif unit_vec[2] < 0:
                dec = -pi / 2
            else:
                raise RuntimeError('Vector is all zeros')
            ra = 0
        else:
            ra = atan2(unit_vec[1], unit_vec[0])
            dec = asin(unit_vec[2])

        return ra, dec


class ConicalFOV(FieldOfView):
    def __init__(self, attached_object: gp.Imager | gp.Antenna, name: str = 'DefaultConicalFOV', color: list = None,
                 fov_angle: int | float = 30):
        super().__init__(attached_object, 'ConicalFOV', name)

        self.color = [float(ele) for ele in self.GetField('Color')[1:-1].split(' ')]
        if color is None:
            # color: list = [0, 0, 0]
            color = gp.Color()
        self.color = color  # None case already handled above

        self.fov_angle = fov_angle if fov_angle is not None else 30
        self.SetRealParameter('FieldOfViewAngle', self.fov_angle)

    def CheckTargetVisibility(self):
        raise NotImplementedError


class CustomFOV(FieldOfView):
    def __init__(self, attached_object: gp.Imager | gp.Antenna, name: str = 'DefaultCustomFOV'):
        super().__init__(attached_object, 'CustomFOV', name)

    def CheckTargetVisibility(self):
        raise NotImplementedError


class RectangularFOV(FieldOfView):
    def __init__(self, attached_object: gp.Imager | gp.Antenna, name: str = 'DefaultRectangularFOV',
                 angle_width: int | float = None, angle_height: int | float = None):
        super().__init__(attached_object, 'RectangularFOV', name)

        self._boresight = self.attached_obj.boresight  # inherit boresight from attached Imager/Antenna

        # TODO set second_vec

        # Set initial angle width, in degrees
        if angle_width is None:
            self._angle_width = self.GetRealParameter('AngleWidth')  # use underscore variant to not re-set in GMAT obj
        else:
            self.angle_width = angle_width  # RealParameter set in angle_width.setter

        # Set initial angle height, in degrees
        if angle_height is None:
            self._angle_height = self.GetRealParameter('AngleHeight')  # underscore variant to not re-set in GMAT obj
        else:
            self.angle_height = angle_height  # RealParameter set in angle_height.setter

        self.Initialize()

    @property
    def angle_height(self) -> float | int:
        return self._angle_height

    @angle_height.setter
    def angle_height(self, angle_height: int | float):
        self._angle_height = angle_height
        self.SetRealParameter('AngleHeight', angle_height)

    @property
    def angle_width(self) -> float | int:
        return self._angle_width

    @angle_width.setter
    def angle_width(self, angle_width: int | float):
        self._angle_width = angle_width
        self.SetRealParameter('AngleWidth', angle_width)

    @property
    def boresight(self):
        return self._boresight

    @boresight.setter
    def boresight(self, new_boresight: np.ndarray | list):
        if not isinstance(new_boresight, np.ndarray):
            new_boresight = np.array(new_boresight)

        self._boresight = new_boresight
        # TODO add second_vec and rotation_matrix updating as in Imager.boresight.setter

    def CheckTargetVisibility(self, target: np.ndarray) -> bool:
        ra, dec = self.UnitVecToRADEC(target)
        cone, clock = self.RADECtoConeClock(ra, dec)

        angle_height = self.GetRealParameter('AngleHeight')
        angle_width = self.GetRealParameter('AngleWidth')

        # using <= assures that 0 width, 0 height FOV never has point in FOV
        # if you want (0.0,0.0) to always be in FOV change to strict inequalities
        if (cone >= angle_height) or (cone <= -angle_height) or (clock >= angle_width) or (clock <= -angle_width):
            return False
        else:
            return True

    def CustomCheckTargetVisibility(self, target: np.ndarray | list) -> bool:
        """Determine whether a point is within the Imager's field of view.

        Note: this currently assumes that the Y-axis is the boresight, the X-axis is towards the right of the FOV, and
        the Z-axis is pointing up in the FOV. The origin is taken to be the center of the Imager's sensor/FOV.
        # TODO: change this to match GMAT, which uses z for boresight, v for second_vec, x for normalized version of normal to z and v (N), y as z cross x.

        Overall process:
        1) Find the vectors that give the edges of the FOV
        2) Find the normal vector to each pair of adjacent vectors such that the normal points into the FOV
        3) The target is in the FOV if the dot product of the target's position vector and the normal vector is
        positive, for all four of the normal vectors.

        :param target: np array or list representation of a 3D position vector for the target point, in the spacecraft body frame.
        :return in_fov: bool - True if target is in field of view, False if not.
        :rtype: bool
        """

        # Note: GMAT handles Imagers as having no sensor width/height, so FOV edge vectors start at origin rather than
        #  being translated by sensor width/2, sensor height/2 etc.

        # TODO determine whether applicable to FOVs with width/height >180 degrees

        # TODO consider case where FOV rolled around boresight - need to update axes so midpoint vecs calced correctly

        # Check target position vector is valid
        if len(target) != 3:
            raise AttributeError(f'target has an invalid number of elements ({len(target)}) - must be 3 to represent a '
                                 f'3D position vector for the target point')
        # Convert target to numpy array if it's a list to use numpy's better performance
        if isinstance(target, list):
            target: np.ndarray = np.array(target)

        # TODO: transform target from spacecraft body frame to Imager frame (using Imager rotation matrix?)
        print('\n** WARNING: CustomCheckTargetVisibility does not currently convert the target to the Imager frame, so '
              'its result is likely to be incorrect **\n')

        aw2 = self.angle_width / 2
        ah2 = self.angle_height / 2

        # Each face of FOV has a vector along its midpoint. Find the normal vectors to these that point into FOV.
        # Parameters for vectors normal to FOV face midpoint vectors
        normals_vector_params = (('Z', np.deg2rad(aw2 - 90)),
                                 ('Z', np.deg2rad(-aw2 + 90)),
                                 ('Y', np.deg2rad(-ah2 + 90)),
                                 ('Y', np.deg2rad(ah2 - 90)))
        normals = []  # empty list to hold normal vectors
        for vec_param in normals_vector_params:  # rotate boresight to find each normal vector, using vec's params
            normals.append(gp.rotate_vector(self.boresight, vec_param[0], vec_param[1]))
        normals = np.array(normals)  # convert list of normals to np.ndarray

        # If the target is within the FOV, the normal will point more towards the target than away. This means the dot
        # product of the normal and the target's position vector will be positive
        dot_results = np.dot(normals, target)

        return True if all(dot_results > 0) else False

    def GetMaskClockAngles(self) -> list:
        angle_width = self.GetRealParameter('AngleWidth')
        return [1, angle_width]

    def GetMaskConeAngles(self):
        # # FIXME - broken because of GmatBase type for self
        # if not degrees:
        #     return self.gmat_obj.GetMaskConeAngles()
        # else:
        #     return self.gmat_obj.GetMaskConeAngles() * 180 / pi
        angle_height = self.GetRealParameter('AngleHeight')
        return [1, angle_height]
