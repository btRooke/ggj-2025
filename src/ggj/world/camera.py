from typing import ClassVar


class Camera:
    pos: ClassVar[list[int]] = [0, 0]

    @staticmethod
    def get_pos() -> tuple[int, int]:
        return (Camera.pos[0], Camera.pos[1])

    @staticmethod
    def move_camera(mov_vec: tuple[int, int]):
        x, y = mov_vec
        Camera.pos[0] += x
        Camera.pos[1] += y
