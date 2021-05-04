from detection.Text import Text
from detection.Element import Element
from detection.Image import Image
from detection.Input import Input
from detection.Table import Table
from detection.Row import Row
import detection.ocr as ocr

import cv2
import time
import numpy as np
import string
import os


def form_compo_detection(form_img_file_name, resize_height=None, export_dir=None):
    if cv2.imread(form_img_file_name).shape[0] > 1200:
        resize_height = 900
    # *** 1. Basic element detection ***
    form = Form(form_img_file_name, resize_height=resize_height)
    form.text_detection()
    form.element_detection()
    # form.visualize_all_elements()

    # *** 2. Basic element noise removal ***
    form.filter_detection_noises()
    form.text_sentences_recognition()
    form.shrink_text_and_filter_noises()
    form.assign_element_ids()
    # form.visualize_all_elements()

    # *** 3. Special element recognition ***
    form.border_and_textbox_recognition()
    # form.visualize_all_elements()
    form.character_box_recognition()
    # form.visualize_all_elements()

    # *** 4. Units labelling ***
    form.label_elements_as_units()
    form.sort_units()
    form.border_line_recognition()
    # form.visualize_units()

    # *** 5. Form structure recognition ***
    form.check_vertical_aligned_form()
    # form.visualize_vertical_separators()
    form.group_elements_by_separators()
    # form.visualize_unit_groups()

    # *** 6. Table obj ***
    form.table_detection()
    # form.visualize_all_elements()
    form.table_refine()
    # form.visualize_all_elements()

    # *** 7. Input compound recognition ***
    form.input_compound_recognition()
    # form.visualize_detection_result()
    form.input_refine()
    # form.visualize_inputs()
    form.text_refine()
    # form.visualize_detection_result()

    # *** 8. Export ***
    form.export_detection_result_img(export_dir)
    return form


class Form:
    def __init__(self, img_file_name, resize_height=None):
        self.img_file_name = img_file_name
        self.resize_height = resize_height
        self.img = Image(img_file_name, resize_height=resize_height)
        self.form_name = img_file_name.split('/')[-1][:-4]

        # atomic elements
        self.texts = []             # detected by ocr
        self.rectangles = []        # detected by cv
        self.squares = []
        self.lines = []             # detected by cv
        # compound elements
        self.tables = []            # recognize by grouping rectangles
        self.inputs = []            # input elements that consists of guide text (text|textbox) and input filed (rectangle|line)
        self.row_id = 0
        self.table_id = 0

        # units for input, grouped from the above elements
        self.text_units = []    # text (not in box) + textbox
        self.bar_units = []     # rectangles (not textbox) + lines + tables
        self.all_units = []
        self.sorted_left_unit = []
        self.sorted_right_unit = []
        self.sorted_top_unit = []
        self.sorted_bottom_unit = []

        self.vertical_separators = None  # dictionary {left, right, top, bottom}, set None if form is vertical alignment
        self.unit_groups = []  # 3-d list, groups of units segmented by separators, [[[sep1-left-group], [sep1-right-group], [sep1-top-group], [sep1-bottom-group]]]

        self.detection_result_img = None
        self.export_dir = 'data/output/' + self.form_name
        os.makedirs(self.export_dir, exist_ok=True)

    '''
    ****************************
    *** Check Form Structure ***
    ****************************
    '''
    def check_vertical_aligned_form(self):
        '''
        Check if the form is vertical aligned
        :return: set self.vertical_separator if the form is in vertical alignment
        '''

        def check_gaps_from_mid(binary):
            '''
            Check continuously connected gap in columns from the middle leftwards and rightwards
            :param binary: binary map of the form image
            :return: {'left': {col_id1: [(gap1_top, gap1_bottom), (gap2_top, gap2_bottom)],
                    'right': {col_id1: [(gap1_top, gap1_bottom), (gap2_top, gap2_bottom)],
                    'mid': {mid_col_id: [(gap1_top, gap1_bottom), (gap2_top, gap2_bottom)]}}
            '''
            def check_gaps_in_a_col(col):
                col_gaps = []
                gap_top = -1
                gap_bottom = -1
                for i in range(height - 1):
                    if binary[i, col] == 0:
                        if gap_top == -1:
                            gap_top = i
                    else:
                        if gap_top != -1:
                            gap_bottom = i - 1
                            if gap_bottom - gap_top > height / 3:
                                col_gaps.append((gap_top, gap_bottom))
                            gap_top = -1
                            gap_bottom = -1
                if gap_bottom <= gap_top:
                    gap_top = max(0, gap_top)
                    gap_bottom = height - 1
                    if gap_bottom - gap_top > height / 3:
                        col_gaps.append((gap_top, gap_bottom))
                return col_gaps

            (height, width) = binary.shape
            mid = int(width / 2)
            right = mid + 1
            left = mid - 1
            gap_mid = check_gaps_in_a_col(mid)
            gap_right = check_gaps_in_a_col(right)
            gap_left = check_gaps_in_a_col(left)
            gaps = {'mid': {mid: gap_mid}, 'left': {}, 'right': {}}

            spreading = True
            while spreading:
                spreading = False
                if len(gap_right) > 0:
                    gaps['right'][right] = gap_right
                    right = right + 1
                    if right < width - 1:
                        gap_right = check_gaps_in_a_col(right)
                        spreading = True
                if len(gap_left) > 0:
                    gaps['left'][left] = gap_left
                    left = left - 1
                    if left > 0:
                        gap_left = check_gaps_in_a_col(left)
                        spreading = True
            return gaps

        def merge_gaps_as_separators(gaps):
            '''
            merge the detected gaps as vertical separators
            :return: list of separators: [{'top', 'bottom', 'left', 'right'}]
            '''
            gaps_m = gaps['mid']
            gaps_left = gaps['left']
            gaps_right = gaps['right']
            mid_col_id = list(gaps_m.keys())[0]
            left_col_ids = sorted(list(gaps_left.keys()), reverse=True)
            right_col_ids = sorted(list(gaps_right.keys()))

            gm = gaps_m[mid_col_id]
            merged_gap = {}
            for g in gm:
                merged_gap[g] = {'left': mid_col_id, 'right': mid_col_id, 'top': g[0], 'bottom': g[1]}

            for i in left_col_ids:
                gl = gaps_left[i]
                # match all gaps between gaps of the mid col and gaps in this col
                for a in gm:
                    for b in gl:
                        if abs(a[0] - b[0]) < 10 and abs(a[1] - b[1]) < 10:
                            if merged_gap[a]['left'] - i == 1:
                                merged_gap[a]['left'] = i
                                merged_gap[a]['top'] = max(merged_gap[a]['top'], b[0])
                                merged_gap[a]['bottom'] = min(merged_gap[a]['bottom'], b[1])

            for i in right_col_ids:
                gl = gaps_right[i]
                # match all gaps between gaps of the mid col and gaps in this col
                for a in gm:
                    for b in gl:
                        if abs(a[0] - b[0]) < 10 and abs(a[1] - b[1]) < 10:
                            if i - merged_gap[a]['right'] == 1:
                                merged_gap[a]['right'] = i
                                merged_gap[a]['top'] = max(merged_gap[a]['top'], b[0])
                                merged_gap[a]['bottom'] = min(merged_gap[a]['bottom'], b[1])

            # reformat as list of separators: [{'top', 'bottom', 'left', 'right'}]
            separators = []
            for k in merged_gap:
                separators.append(merged_gap[k])
            return separators

        all_gaps = check_gaps_from_mid(self.img.binary_map)
        # print(all_gaps)
        separators = merge_gaps_as_separators(all_gaps)
        if len(separators) > 0:
            print('*** The form is vertical alignment with vertical separators:', separators, '***')
            self.vertical_separators = separators
        else:
            print('*** The form is not vertical alignment ***')
            self.vertical_separators = None

    def group_elements_by_separators(self):
        '''
        If the form is vertical alignment Group all units by separators
        For each separator, it can segment four groups of units [[left-group], [right-group], [top-group], [bottom-group]]
        :return: [[[sep1-left-group], [sep1-right-group], [sep1-top-group], [sep1-bottom-group]]]
        '''
        # only for vertical aligned form
        if self.vertical_separators is None:
            return
        seps = self.vertical_separators
        groups = []
        for i in range(len(seps)):
            groups.append([[], [], [], []])

        for p, ele in enumerate(self.get_all_elements()):
            for i, sep in enumerate(seps):
                if ele.location['bottom'] <= sep['top']:
                    if i == 0 or ele.location['top'] > seps[i - 1]['bottom']:
                        ele.unit_group_id = i * 4 + 0
                        groups[i][0].append(ele)
                elif sep['top'] < ele.location['top'] and ele.location['bottom'] <= sep['bottom']:
                    if ele.location['right'] <= sep['left']:
                        ele.unit_group_id = i * 4 + 1
                        groups[i][1].append(ele)
                    elif ele.location['left'] > sep['right']:
                        ele.unit_group_id = i * 4 + 2
                        groups[i][2].append(ele)
                else:
                    ele.unit_group_id = i * 4 + 3
                    groups[i][3].append(ele)
        self.unit_groups = groups

    '''
    **************************
    *** Element Processing ***
    **************************
    '''
    def get_all_elements(self):
        return self.texts + self.rectangles + self.squares + self.lines

    def assign_element_ids(self):
        '''
        Assign an unique id to each element and store the id mapping
        '''
        for i, ele in enumerate(self.get_all_elements()):
            ele.id = i

    def get_detection_result(self):
        '''
        Get all non-noisy independent elements (not in any modules) and modules (table, input compound)
        :return: A list of Elements
        '''
        detection_result = []
        for text in self.texts:
            if not text.in_box and not text.is_abandoned and not text.is_module_part:
                detection_result.append(text)

        for rec in self.rectangles:
            if not rec.is_abandoned and not rec.is_module_part:
                detection_result.append(rec)

        for squ in self.squares:
            if not squ.is_abandoned and not squ.is_module_part:
                detection_result.append(squ)

        for line in self.lines:
            if not line.is_abandoned and not line.is_module_part:
                detection_result.append(line)

        for table in self.tables:
            detection_result.append(table)

        for ipt in self.inputs:
            detection_result.append(ipt)

        return detection_result

    def sort_units(self):
        '''
        Sort all units by left and top respectively, and store the result in id lists
        '''
        self.sorted_left_unit = sorted(self.all_units, key=lambda x: x.location['left'])
        self.sorted_right_unit = self.sorted_left_unit.copy()
        self.sorted_right_unit.reverse()

        self.sorted_top_unit = sorted(self.all_units, key=lambda x: x.location['top'])
        self.sorted_bottom_unit = self.sorted_top_unit.copy()
        self.sorted_bottom_unit.reverse()

    def label_elements_as_units(self):
        '''
        text_units: text (not contained) + textbox
        bar_units: rectangles (not textbox) + lines + tables
        '''
        self.text_units = []  # text (not in box) + textbox
        self.bar_units = []  # rectangles (not textbox) + lines + tables
        self.all_units = []
        for text in self.texts:
            if not text.in_box and not text.is_abandoned:
                text.unit_type = 'text_unit'
                self.text_units.append(text)
        for ele in self.rectangles + self.squares + self.lines:
            if ele.is_abandoned:
                continue
            if ele.type in ('line', 'rectangle', 'square'):
                ele.unit_type = 'bar_unit'
                self.bar_units.append(ele)
            elif ele.type == 'textbox':
                ele.unit_type = 'text_unit'
                self.text_units.append(ele)
        self.all_units = self.text_units + self.bar_units

    def find_neighbour_unit(self, unit, direction='right', connect_bias=10, align_bias=4):
        '''
        Find the first unit 1.next to and 2.in alignment with the target
        :param direction:
            -> left: find left neighbour
            -> right: find right neighbour
            -> top: find top neighbour
            -> below: find below neighbour
        :return:
        '''
        if direction == 'right':
            if unit.neighbour_right is not None:
                return unit.neighbour_right
            # check is there any connected unit on the right
            for u in self.sorted_left_unit:
                if u.id != unit.id and u.unit_group_id == unit.unit_group_id and\
                        u.location['left'] + connect_bias >= unit.location['right']:
                    # the tow should be justified
                    if unit.is_in_alignment(u, direction='h', bias=align_bias):
                        unit.neighbour_right = u
                        u.neighbour_left = unit
                        return u
        elif direction == 'left':
            if unit.neighbour_left is not None:
                return unit.neighbour_left
            # check is there any connected unit on the left
            for u in self.sorted_right_unit:
                if u.id != unit.id and u.unit_group_id == unit.unit_group_id and\
                        unit.location['left'] + connect_bias >= u.location['right']:
                    # the tow should be justified
                    if unit.is_in_alignment(u, direction='h', bias=align_bias):
                        unit.neighbour_left = u
                        u.neighbour_right = unit
                        return u
        elif direction == 'below':
            if unit.neighbour_bottom is not None:
                return unit.neighbour_bottom
            # check is there any connected unit below
            for u in self.sorted_top_unit:
                if u.id != unit.id and u.unit_group_id == unit.unit_group_id and\
                        u.location['top'] + connect_bias >= unit.location['bottom']:
                    # the tow should be justified if they are neighbours
                    if unit.is_in_alignment(u, direction='v', bias=align_bias):
                        unit.neighbour_bottom = u
                        u.neighbour_top = unit
                        return u
        elif direction == 'top':
            if unit.neighbour_top is not None:
                return unit.neighbour_top
            # check is there any connected unit above
            for u in self.sorted_bottom_unit:
                if u.id != unit.id and u.unit_group_id == unit.unit_group_id and\
                        unit.location['top'] + connect_bias >= u.location['bottom']:
                    # the tow should be justified if they are neighbours
                    if unit.is_in_alignment(u, direction='v', bias=align_bias):
                        unit.neighbour_top = u
                        u.neighbour_bottom = unit
                        return u
        return None

    '''
    *************************
    *** Element Detection ***
    *************************
    '''
    def text_detection(self, method='Google'):
        if method == 'Baidu':
            self.Baidu_OCR_text_detection()
        elif method == 'Google':
            self.Google_OCR_text_detection()

    def Baidu_OCR_text_detection(self):
        start = time.clock()
        detection_result = ocr.ocr_detection_baidu(self.img_file_name)
        texts = detection_result['words_result']
        for text in texts:
            location = {'left': text['location']['left'], 'top': text['location']['top'],
                        'right': text['location']['left'] + text['location']['width'],
                        'bottom': text['location']['top'] + text['location']['height']}
            self.texts.append(Text(text['words'], location))
        print('*** Baidu OCR Processing Time:%.3f s***' % (time.clock() - start))

    def Google_OCR_text_detection(self):
        start = time.clock()
        detection_results = ocr.ocr_detection_google(self.img.img)
        if detection_results is not None:
            for result in detection_results:
                x_coordinates = []
                y_coordinates = []
                text_location = result['boundingPoly']['vertices']
                text = result['description']
                for loc in text_location:
                    x_coordinates.append(loc['x'])
                    y_coordinates.append(loc['y'])
                location = {'left': min(x_coordinates), 'top': min(y_coordinates),
                            'right': max(x_coordinates), 'bottom': max(y_coordinates)}
                # if location['right'] - location['left'] >= 1 and location['bottom'] - location['top'] >= 1:
                #     self.texts.append(Text(text, location))
                self.texts.append(Text(text, location))
        print('*** Google OCR Processing Time:%.3f s***' % (time.clock() - start))

    def text_sentences_recognition(self):
        '''
        Merge separate words detected by Google ocr into a sentence
        '''
        changed = True
        while changed:
            changed = False
            temp_set = []
            for text_a in self.texts:
                merged = False
                for text_b in temp_set:
                    if text_a.is_on_same_line(text_b, 'h', bias_justify=3, bias_gap=15):
                        text_b.merge_text(text_a)
                        merged = True
                        changed = True
                        break
                if not merged:
                    temp_set.append(text_a)
            self.texts = temp_set.copy()

    def shrink_text_and_filter_noises(self):
        noises = []
        for text in self.texts:
            text.shrink_bound(self.img.binary_map)
            if min(text.width, text.height) <= 3:
                text.is_abandoned = True
                noises.append(text)
        for n in noises:
            self.texts.remove(n)

    def element_detection(self):
        start = time.clock()
        self.rectangles, self.squares = self.img.detect_rectangle_and_square_elements()
        self.lines = self.img.detect_line_elements()
        print('*** Element Detection Time:%.3f s***' % (time.clock() - start))

    def filter_detection_noises(self):
        # count shapes contained in text as noise
        rects = self.rectangles.copy()
        squs = self.squares.copy()
        lines = self.lines.copy()
        for text in self.texts:
            if text.area == 0:
                continue
            for rec in self.rectangles:
                if text.pos_relation(rec) == 1:
                    rects.remove(rec)
            for line in self.lines:
                if text.pos_relation(line) == 1:
                    lines.remove(line)
            # if a square is in a text, store it in text.contain_square
            for squ in self.squares:
                if squ.pos_relation(text) == -1:
                    if squ.area / text.area < 0.6 and abs(squ.location['left'] - text.location['left']) < 5:
                        text.location['left'] = squ.location['right']
                    else:
                        squs.remove(squ)
            self.rectangles = rects.copy()
            self.squares = squs.copy()
            self.lines = lines.copy()

        # filter out double nested shapes
        redundant_nesting = []
        rect_squs = self.rectangles + self.squares
        for i, rect_squ in enumerate(rect_squs):
            containment_area = 0
            containments = []
            for j in range(i + 1, len(rect_squs)):
                ioi, ioj = rect_squ.calc_intersection(rect_squs[j])
                if ioj == 1:
                    containment_area += rect_squs[j].area
                    containments.append(rect_squs[j])
            # if containment_area / rect_squ.area > 0:
            #     print(len(containments), containment_area, rect_squ.area, containment_area / rect_squ.area)
            #     rect_squ.visualize_element(self.get_img_copy(), show=True)
            if containment_area / rect_squ.area > 0.5:
                rect_squ.is_abandoned = True
                redundant_nesting.append(rect_squ)
        for r in redundant_nesting:
            if r.type == 'rectangle':
                self.rectangles.remove(r)
            elif r.type == 'square':
                self.squares.remove(r)

    '''
    ***********************************
    *** Special Element Recognition ***
    ***********************************
    '''
    def border_and_textbox_recognition(self):
        '''
        If a rectangle contains only texts in it, then label the rect as type of 'textbox'
        Else if it contains other rectangles in it, then label it as type of 'border'
        '''
        all_eles = self.get_all_elements()
        # iteratively check the relationship between eles and rectangles
        for ele in all_eles:
            for rec_squ in self.rectangles + self.squares:
                if ele.id == rec_squ.id:
                    continue
                relation = ele.pos_relation(rec_squ)
                # if the element is contained in the rectangle box
                if relation == -1:
                    if rec_squ not in ele.contains:
                        rec_squ.contains.append(ele)
                        rec_squ.containment_area += ele.area

        for rec_squ in self.rectangles + self.squares:
            rs_type = rec_squ.is_textbox_or_border()
            # merge text vertically for a textbox
            if rs_type == 'textbox':
                for containment in rec_squ.contains:
                    containment.in_box = True
                rec_squ.textbox_merge_and_extract_texts_content()

    def border_line_recognition(self):
        '''
        Recognize if a rectangle/line is a nonfunctional border line
        '''
        borders = []
        for bar in self.bar_units:
            if bar.type == 'line':
                neighbour = self.find_neighbour_unit(bar, direction='top')
                if abs(neighbour.location['left'] - bar.location['left']) > 5 or\
                        bar.location['top'] - neighbour.location['bottom'] < 10:
                    bar.type = 'border'
                    bar.unit_type = None
                    borders.append(bar)
        for bar in borders:
            self.bar_units.remove(bar)
            self.all_units.remove(bar)
        self.sort_units()

    def character_box_recognition(self):
        '''
        Recognize if some rectangles and squares can combine into a character box
        '''
        rect_squs = self.rectangles + self.squares

        changed = True
        while changed:
            changed = False
            temp_set = []
            for r1 in rect_squs:
                merged = False
                for r2 in temp_set:
                    if r2.is_in_same_character_box(r1):
                        r2.character_box_merge_ele(r1)
                        merged = True
                        changed = True
                        break
                if not merged:
                    temp_set.append(r1)
            rect_squs = temp_set.copy()

        self.rectangles = []
        self.squares = []
        for rect_squ in rect_squs:
            if rect_squ.type in ('rectangle', 'textbox'):
                self.rectangles.append(rect_squ)
            elif rect_squ.type == 'square':
                self.squares.append(rect_squ)

    '''
    *************************************
    *** Compound Components Detection ***
    *************************************
    '''
    def input_compound_recognition(self, max_gap_h=100, max_gap_v=20, max_left_justify=8):
        '''
        Recognize input unit that consists of [guide text] and [input field]
        First. recognize guide text for input:
            If a text_unit's closet element in alignment is bar_unit, then count it as a guide text
        Second. compound the guide text and its bar unit (input field) as an Input element
        '''
        section_keywords = {'part', 'section'}
        # *** 1. Embedded Input: input field and guiding text in the same rectangle ***
        for textbox in self.text_units:
            if textbox.type == 'textbox' and not textbox.is_text_contain_words(section_keywords) and textbox.in_input is None and textbox.in_table is None:
                if 0 < len(textbox.contains) <= 2:
                    guiding_text = textbox.contains[0]
                    content = guiding_text.content
                    if content.count(':') == 1 and content.count('.') <= 1:
                        self.inputs.append(Input(guiding_text, textbox, is_embedded=True))
                        continue

                # *** 2. A small piece of text at corner of a large Input box ***
                ratio = 2 if max([c.height for c in textbox.contains]) > 20 else 4
                if textbox.height / max([c.height for c in textbox.contains]) > ratio and 0 < textbox.containment_area / textbox.area < 0.15:
                    if min([c.location['left'] for c in textbox.contains]) - textbox.location['left'] > textbox.location['right'] - max([c.location['right'] for c in textbox.contains]) and\
                            min([c.location['top'] for c in textbox.contains]) - textbox.location['top'] > textbox.location['bottom'] - max([c.location['bottom'] for c in textbox.contains]):
                        neighbour_top = self.find_neighbour_unit(textbox, 'top')
                        if neighbour_top is not None and neighbour_top.unit_type == 'text_unit' and neighbour_top.in_input is None and neighbour_top.in_table is None and \
                                textbox.location['top'] - neighbour_top.location['bottom'] < max_gap_v:
                            textbox.type = 'rectangle'
                            self.inputs.append(Input(neighbour_top, textbox, placeholder=textbox.content))
                    else:
                        self.inputs.append(Input(textbox.contains[0], textbox, is_embedded=True))

        # *** 3. Normal Input: guide text and input field are separate and aligned ***
        # from left to right
        units = self.sorted_left_unit
        for i, unit in enumerate(units):
            if unit.unit_type == 'text_unit' and unit.in_input is None and unit.in_table is None:
                neighbour_right = self.find_neighbour_unit(unit, direction='right', align_bias=0)
                if neighbour_right is not None and\
                        neighbour_right.unit_type == 'bar_unit' and neighbour_right.type != 'square' and\
                        neighbour_right.in_input is None and neighbour_right.in_table is None and\
                        neighbour_right.location['left'] - unit.location['right'] < max_gap_h:
                    self.inputs.append(Input(unit, neighbour_right))
        # from top to bottom
        units = self.sorted_top_unit
        for i, unit in enumerate(units):
            if unit.unit_type == 'text_unit' and unit.in_input is None and unit.in_table is None:
                neighbour_below = self.find_neighbour_unit(unit, direction='below', align_bias=0)
                # units of an input compound with vertical alignment should be left justifying
                if neighbour_below is not None and\
                        neighbour_below.unit_type == 'bar_unit' and neighbour_below.type != 'square' and\
                        neighbour_below.in_input is None and neighbour_below.in_table is None and\
                        neighbour_below.location['top'] - unit.location['bottom'] < max_gap_v:
                    # if the bar has text above justified
                    if abs(unit.location['left'] - neighbour_below.location['left']) < max_left_justify:
                        self.inputs.append(Input(unit, neighbour_below))
                    # if the bar has no left or right neighbour, then combine it with text above
                    else:
                        bar_left = self.find_neighbour_unit(neighbour_below, direction='left')
                        bar_right = self.find_neighbour_unit(neighbour_below, direction='right')
                        if bar_left is None and bar_right is None:
                            self.inputs.append(Input(unit, neighbour_below))

        # *** 4. Checkbox: a square following/followed by a guide text
        for bar in self.bar_units:
            if bar.type == 'square' and bar.in_input is None and bar.in_table is None:
                if bar.nesting_text is not None:
                    self.inputs.append(Input(bar.nesting_text, bar, is_checkbox=True))
                    continue
                # check square's left and right, and chose the
                neighbour_right = self.find_neighbour_unit(bar, direction='right', align_bias=0)
                neighbour_left = self.find_neighbour_unit(bar, direction='left', align_bias=0)
                if neighbour_right is not None and neighbour_right.unit_type == 'text_unit' and neighbour_right.in_input is None and neighbour_right.in_table is None:
                    if neighbour_left is not None and neighbour_left.unit_type == 'text_unit' and neighbour_left.in_input is None and neighbour_left.in_table is None:
                        # check the closer text as guidetext
                        if neighbour_right.location['left'] - bar.location['right'] > bar.location['left'] - neighbour_left.location['right']:
                            self.inputs.append(Input(neighbour_left, bar, is_checkbox=True))
                        else:
                            self.inputs.append(Input(neighbour_right, bar, is_checkbox=True))
                    else:
                        self.inputs.append(Input(neighbour_right, bar, is_checkbox=True))
                else:
                    if neighbour_left is not None and neighbour_left.unit_type == 'text_unit' and neighbour_left.in_input is None and neighbour_left.in_table is None:
                        self.inputs.append(Input(neighbour_left, bar, is_checkbox=True))

    def row_detection(self, unit):
        '''
        Detect row through grouping all left-right connected and justified elements
        :param unit: start unit
        '''
        # if already are detected in a row
        if unit.in_row is not None:
            return unit.in_row
        unit_org = unit

        row = Row(self.row_id)
        self.row_id += 1
        # right forward
        neighbour_right = self.find_neighbour_unit(unit, 'right')
        is_row = False
        # if there is a connected neighbour, add it and the current unit to a Row
        while neighbour_right is not None and unit.is_on_same_line(neighbour_right, 'h', bias_gap=10)\
                and neighbour_right.unit_type == 'bar_unit':
            if not is_row:
                row.add_element(unit)
                is_row = True
            # if the neighbour is already in a row, then simply add the current one to the row
            if neighbour_right.in_row is not None:
                row.merge_row(neighbour_right.in_row)
                break
            row.add_element(neighbour_right)
            unit = neighbour_right
            neighbour_right = self.find_neighbour_unit(neighbour_right, 'right')

        # left forward
        unit = unit_org
        neighbour_left = self.find_neighbour_unit(unit, 'left')
        # if there is neighbour on the same row, add it and the current unit to a Row
        while neighbour_left is not None and unit.is_on_same_line(neighbour_left, 'h', bias_gap=10)\
                and neighbour_left.unit_type == 'bar_unit':
            if not is_row:
                row.add_element(unit)
                is_row = True
            # if the neighbour is already in a row, then simply add the current one to the row
            if neighbour_left.in_row is not None:
                row.merge_row(neighbour_left.in_row)
                break
            row.add_element(neighbour_left)
            unit = neighbour_left
            neighbour_left = self.find_neighbour_unit(neighbour_left, 'left')

        if len(row.elements) > 1:
            # row.visualize_row(self.img.img.copy(), show=True)
            return row
        else:
            return None

    def detect_table_heading(self, table, max_gap=20):
        '''
        Detect heading row for each table
        :param max_gap: max gop between the top row of a table and its top neighbour
        '''
        neighbours = []
        top_row = table.rows[0]
        # record all neighbours above the top row elements
        for ele in top_row.elements:
            n = self.find_neighbour_unit(ele, direction='top')
            if n is not None and \
                    n.unit_type == 'text_unit' and abs(ele.location['top'] - n.location['bottom']) < max_gap:
                neighbours.append(n)
            else:
                neighbours.append(None)

        heading = Row(row_id=self.row_id)
        self.row_id += 1
        for ele in neighbours:
            if ele is not None:
                heading.add_element(ele)
        if heading.location is not None:
            table.add_heading(heading)

    def detect_table_row_title(self, table, max_title_justify_bias=10):
        titles = []
        t_num = 0
        for row in table.rows:
            first_ele = row.elements[0]
            neighbour = self.find_neighbour_unit(first_ele, direction='left')
            if neighbour is not None and neighbour.unit_type == 'text_unit' and neighbour.in_input is None and neighbour.in_table is None:
                titles.append(neighbour)
                t_num += 1
            else:
                titles.append(None)

        if t_num / len(table.rows) >= 0.5:
            for i in range(1, len(titles)):
                if titles[i] is None or titles[i - 1] is None:
                    continue
                if abs(titles[i].location['left'] - titles[i - 1].location['left']) > max_title_justify_bias:
                    return
            for i, title in enumerate(titles):
                if title is not None:
                    table.rows[i].row_title = title
                    title.is_module_part = True
                    table.rows[i].add_element(title)
                    table.sort_rows()
                    table.init_bound()

    def table_detection(self):
        '''
        Detect table by detecting continuously matched rows
        '''
        recorded_row_ids = []
        for unit in self.all_units:
            if unit.unit_type == 'bar_unit':
                # if an element has right(same row) and below(same column) connected elements
                # then check if its row and the row below it are matched
                row = self.row_detection(unit)
                if row is not None:
                    # avoid redundancy
                    if row.row_id in recorded_row_ids:
                        continue
                    else:
                        recorded_row_ids.append(row.row_id)

                    if row.parent_table is not None:
                        continue
                    else:
                        table = Table(self.table_id)
                        self.table_id += 1

                    # *** detect down forwards ***
                    unit_a = unit
                    unit_b = self.find_neighbour_unit(unit_a, 'below')
                    if unit_b is None or unit_b.unit_type != 'bar_unit':
                        continue
                    row_a = row
                    # check if the unit has neighbour on the same colunm
                    while unit_b is not None and unit_a.is_on_same_line(ele_b=unit_b, direction='v'):
                        row_b = self.row_detection(unit_b)
                        # check if its row and the row below it matches
                        # merge matched parts of the two rows to a table
                        if row_b is not None and row_a.is_matched(row_b):
                            if row_b.parent_table is not None:
                                table.merge_table(row_b.parent_table)
                            else:
                                if table.is_empty():
                                    table.add_rows([row_a, row_b])
                                else:
                                    table.add_row(row_b)
                            unit_a = unit_b
                            row_a = row_b
                            unit_b = self.find_neighbour_unit(unit_a, 'below')
                        else:
                            break

                    # *** detect up forwards ***
                    unit_a = unit
                    unit_b = self.find_neighbour_unit(unit_a, 'top')
                    if unit_b is None or unit_b.unit_type != 'bar_unit':
                        continue
                    row_a = row
                    # check if the unit has neighbour on the same colunm
                    while unit_b is not None and unit_a.is_on_same_line(unit_b, direction='v'):
                        row_b = self.row_detection(unit_b)
                        # check if its row and the row below it matches
                        # merge matched parts of the two rows to a table
                        if row_b is not None and row_a.is_matched(row_b):
                            if row_b.parent_table is not None:
                                table.merge_table(row_b.parent_table)
                            else:
                                if table.is_empty():
                                    table.add_rows([row_a, row_b])
                                else:
                                    table.add_row(row_b)
                            unit_a = unit_b
                            row_a = row_b
                            unit_b = self.find_neighbour_unit(unit_a, 'top')
                        else:
                            break

                    if not table.is_empty():
                        # board = self.get_img_copy()
                        # table.visualize_table(board)
                        # unit.visualize_element(board, color=(0,0,255), show=True)
                        self.tables.append(table)

        return self.tables

    '''
    *************************
    *** Module Refinement ***
    *************************
    '''
    def table_merge_contained_eles(self, table):
        '''
        Merge elements that are not grouped but contained in the table
        '''
        for unit in self.all_units:
            if unit.in_row is not None or unit.in_table is not None:
                continue
            if table.is_ele_contained_in_table(unit):
                table.insert_element(unit)

    def table_refine(self):
        # *** Step 1. Merge elements that are not grouped but contained in a table ***
        for table in self.tables:
            self.table_merge_contained_eles(table)

        # *** Step 2. Heading detection for table ***
        for table in self.tables:
            self.detect_table_heading(table)
            self.table_merge_contained_eles(table)
            table.merge_vertical_texts_in_cell()

        # *** Step 3. Split columns of a table according to the heading ***
        for table in self.tables:
            table.split_columns()

        # *** Step 4. Detect row title for each row ***
        for table in self.tables:
            self.detect_table_row_title(table)
            self.table_merge_contained_eles(table)
            table.merge_vertical_texts_in_cell()

        # *** Step 5. Remove noises according to column ***
        for table in self.tables:
            table.rm_noisy_element()

    def input_refine(self):
        # if the only contained text contains certain keyword, label it as input
        input_keywords = {'name', 'names', 'date', 'id'}
        for text in self.text_units:
            if not text.is_module_part and not text.is_abandoned:
                words = [c.lower() for c in text.content.split(' ')]
                if 1 < len(words) <= 5 and len(set(words) & input_keywords) > 0:
                    if text.type == 'textbox':
                        self.inputs.append(Input(text.contains[0], text))
                    elif text.type == 'text':
                        self.inputs.append(Input(text, text))

        for ipt in self.inputs:
            # skip inputs where its guide text and input filed in the same box
            if ipt.is_embedded:
                continue
            # merge intersected text into guide_text
            changed = True
            while changed:
                changed = False
                for text in self.text_units:
                    if not text.is_module_part and not text.is_abandoned and\
                            ipt.guide_text.unit_group_id == text.unit_group_id and\
                            (ipt.guide_text.pos_relation(text, bias=2) != 0 or ipt.pos_relation(text, bias=2) != 0):
                        ipt.merge_guide_text(text)
                        changed = True
                        break

            # merged connected input field horizontally
            changed = True
            while changed:
                changed = False
                for bar in self.bar_units:
                    if not bar.is_module_part and not bar.is_abandoned and bar.type == 'rectangle' and\
                            ipt.is_connected_field(bar, direction='h'):
                        ipt.merge_input_field(bar)
                        changed = True
                        break

        # merged connected input field vertically
        for ipt in self.inputs:
            changed = True
            while changed:
                changed = False
                for bar in self.bar_units:
                    if not bar.is_module_part and not bar.is_abandoned and bar.type == 'rectangle' and\
                            ipt.is_connected_field(bar, direction='v'):
                        ipt.merge_input_field(bar)
                        changed = True
                        break

    def text_refine(self):
        '''
        Merge intersected ungrouped texts
        '''
        texts = []
        others = []
        for text in self.texts:
            if not text.in_box and not text.is_abandoned and not text.is_module_part:
                texts.append(text)
            else:
                others.append(text)

        changed = True
        while changed:
            changed = False
            temp_set = []
            for text_a in texts:
                merged = False
                for text_b in temp_set:
                    if text_a.pos_relation(text_b) != 0:
                        text_b.merge_text(text_a, direction='v')
                        merged = True
                        changed = True
                        break
                if not merged:
                    temp_set.append(text_a)
            texts = temp_set.copy()

        self.texts = texts + others

    '''
    *********************
    *** Visualization ***
    *********************
    '''
    def get_img_copy(self):
        return self.img.img.copy()

    def visualize_vertical_separators(self):
        if self.vertical_separators is None:
            return
        board = self.get_img_copy()
        for separator in self.vertical_separators:
            cv2.rectangle(board, (separator['left'], separator['top']), (separator['right'], separator['bottom']), (0, 255, 0), 1)
        cv2.imshow('v-separators', board)
        cv2.waitKey()
        cv2.destroyWindow('v-separators')

    def visualize_unit_groups(self):
        for group in self.unit_groups:
            for g in group:
                board = self.get_img_copy()
                for u in g:
                    u.visualize_element(board)
                cv2.imshow('groups', board)
                cv2.waitKey()
                cv2.destroyAllWindows()

    def visualize_all_elements(self):
        board = self.get_img_copy()
        for text in self.texts:
            # if not text.in_box and not text.is_abandoned:
            text.visualize_element(board)

        for rec in self.rectangles:
            # if not rec.is_abandoned:
            rec.visualize_element(board)

        for squ in self.squares:
            # if not squ.is_abandoned:
            squ.visualize_element(board)

        for line in self.lines:
            # if not line.is_abandoned:
            line.visualize_element(board)

        for table in self.tables:
            table.visualize_element(board, color=(255,255,0))

        cv2.imshow('form', board)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def visualize_units(self):
        board = self.get_img_copy()
        for text_unit in self.text_units:
            text_unit.visualize_element(board, color=(255, 0, 0))
        for bar_unit in self.bar_units:
            bar_unit.visualize_element(board, color=(0, 255, 0))
        cv2.imshow('Units', board)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def visualize_inputs(self):
        board = self.get_img_copy()
        for ipt in self.inputs:
            ipt.visualize_input(board, line=2)
            # ipt.visualize_input_overlay(board)
            cv2.imshow('Input', board)
            cv2.waitKey()
        cv2.destroyAllWindows()

    def visualize_detection_result(self):
        board = self.get_img_copy()
        for text in self.texts:
            if not text.in_box and not text.is_abandoned and not text.is_module_part:
                text.visualize_element(board)

        for rec in self.rectangles:
            if not rec.is_abandoned and not rec.is_module_part:
                rec.visualize_element(board)

        for line in self.lines:
            if not line.is_abandoned and not line.is_module_part:
                line.visualize_element(board)

        for table in self.tables:
            table.visualize_element(board)

        for ipt in self.inputs:
            ipt.visualize_element(board)

        self.detection_result_img = board
        cv2.imshow('form', board)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def export_detection_result_img(self, export_dir=None):
        board = self.get_img_copy()
        for text in self.texts:
            if not text.in_box and not text.is_abandoned and not text.is_module_part:
                text.visualize_element(board)

        for rec in self.rectangles:
            if not rec.is_abandoned and not rec.is_module_part:
                rec.visualize_element(board)

        for line in self.lines:
            if not line.is_abandoned and not line.is_module_part:
                line.visualize_element(board)

        for table in self.tables:
            table.visualize_element(board, color=(255, 255, 0))

        for ipt in self.inputs:
            ipt.visualize_element(board, color=(255, 0, 255))

        self.detection_result_img = board
        if export_dir is None:
            export_dir = self.export_dir
        print('Write to:', os.path.join(export_dir, self.form_name + '.jpg'))
        cv2.imwrite(os.path.join(export_dir, self.form_name + '.jpg'), board)
