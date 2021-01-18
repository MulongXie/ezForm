import numpy as np
import cv2


class Element:
    def __init__(self,
                 type=None, contour=None, location=None, words=None):
        self.type = type            # text/rectangle/line
        self.contour = contour      # format of findContours

        self.location = location    # dictionary {left, right, top, bottom}
        self.width = None
        self.height = None
        self.get_bound_from_contour()

        self.word = words           # for text

    def get_bound_from_contour(self):
        if self.contour is not None:
            bound = cv2.boundingRect(self.contour)
            self.width = bound[2]
            self.height = bound[3]
            self.location = {'left': bound[0], 'top': bound[2], 'right': bound[0] + bound[2], 'bottom': bound[1] + bound[3]}

    def is_line(self, max_thickness=4):
        if self.height <= max_thickness or self.width <= max_thickness:
            return True
        return False

    def is_rectangle(self):
        '''
        Rectangle recognition by checking slopes between adjacent points
        :param contour: contour
        :return: boolean
        '''
        contour = np.reshape(self.contour, (-1, 2))
        # calculate the slope k (y2-y1)/(x2-x1) the first between two neighboor points
        if contour[0][0] == contour[1][0]:
            k_pre = 'v'
        else:
            k_pre = (contour[0][1] - contour[1][1]) / (contour[0][0] - contour[1][0])

        sides = []
        slopes = []
        side = [contour[0], contour[1]]
        # variables for checking if it's valid to continue using the previous side
        pop_pre = False
        gap_to_pre = 0
        for i, p in enumerate(contour[2:]):
            # calculate the slope k between two neighboor points
            if contour[i][0] == contour[i - 1][0]:
                k = 'v'
            else:
                k = (contour[i][1] - contour[i - 1][1]) / (contour[i][0] - contour[i - 1][0])
            # print(side, k_pre, gap_to_pre)
            # check if the two points on the same side
            if k != k_pre:
                # leave out noises
                if len(side) < 4:
                    # continue using the last side
                    if len(sides) > 0 and k == slopes[-1] \
                            and not pop_pre and gap_to_pre < 4:
                        side = sides.pop()
                        side.append(p)
                        k = slopes.pop()
                        pop_pre = True
                        gap_to_pre = 0
                    # leave out noises
                    else:
                        gap_to_pre += 1
                        side = [p]
                # count as valid side and store it in sides
                else:
                    sides.append(side)
                    slopes.append(k_pre)
                    side = [p]
                    pop_pre = False
                    gap_to_pre = 0
                k_pre = k
            else:
                side.append(p)
        sides.append(side)
        slopes.append(k_pre)
        if len(sides) != 4:
            return False
        # print('Side Number:', len(sides))
        lens = [len(s) for s in sides]
        # print('Side Lengths:', lens, ' Side Slopes:', slopes)
        if (abs(lens[0] - lens[2]) < 4) and (abs(lens[1] - lens[3]) < 4):
            return True
        return False
