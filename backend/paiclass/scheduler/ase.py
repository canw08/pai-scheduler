import multiprocessing
import textwrap, copy, random, time
from multiprocessing import Pool, Process, Manager
from collections import Counter, defaultdict
from itertools import combinations
import heapq
import openpyxl
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Side, Border

class Teacher:
    def __init__(self, n, de=None, ID=None, av=None):
        self.__name = n
        self.__department = de
        self.__id = ID
        self.__avoid = av

    def get_name(self):
        return self.__name

    def get_department(self):
        return self.__department

    def get_teacher_id(self):
        return self.__id

    def get_avoid(self):
        return self.__avoid

class ClassRoom:
    def __init__(self, n, ID=None, cpa=None, posi=None):
        self.__name = n
        self.__id = ID
        self.__capacity = cpa
        self.__position = posi

    def get_name(self):
        return self.__name

    def get_classRoom_id(self):
        return self.__id

    def get_capacity(self):
        return self.__capacity

    def get_position(self):
        return self.__position

class Course:
    def __init__(self, tea, course_name, clsRoom, CNum, id):
        self.__course_teacher = tea
        self.__course_name = course_name
        self.__classRoom = clsRoom
        self.__course_number = CNum
        self.__course_id = id

    def get_teacher(self):
        return self.__course_teacher

    def get_course_name(self):
        return self.__course_name

    def get_courseNum(self):
        return self.__course_number

    def get_classRoom(self):
        return self.__classRoom

    def get_id(self):
        return self.__course_id

class Slot:
    def __init__(self, re=None, total_classRoom_num=None):
        self.__total_classRoom_num = total_classRoom_num
        self.__slot = [None for i in range(total_classRoom_num)]
        #如果是slot6，7 那么就把特殊课程放进这里面
        self.__slot_special = []
        self.__related_slot = re

    def get_slot(self):
        return self.__slot

    def get_related_slot(self):
        return self.__related_slot

    def class_canput(self, course):# 判断一个课程能不能被放到这个slot中
        if course:
            tmp_teacher = course.get_teacher()
            tmp_name = course.get_course_name()
            if course.get_courseNum() > 5:
                if self.__related_slot == None:
                    return False
                slt_course_num = 0
                for cor in self.__related_slot.get_slot():
                    if cor:
                        if cor.get_teacher() == tmp_teacher or cor.get_course_name() == tmp_name:
                            return False
                        slt_course_num += 1
                if (len(self.__related_slot.get_slot_special()) + 1) // 2 + slt_course_num > self.__total_classRoom_num:
                    return False
            elif self.__related_slot == None:
                for cor in self.__slot_special:
                    if cor and (cor.get_teacher() == tmp_teacher or cor.get_course_name() == tmp_name):
                        return False

                slt_course_num = 0
                for cor in self.__slot:
                    if cor:
                        slt_course_num += 1

                if len(self.__slot_special) // 2 + slt_course_num > self.__total_classRoom_num:
                    return False

            for cor in self.__slot:
                if cor and (tmp_teacher == cor.get_teacher() or cor.get_course_name() == tmp_name):
                    return False
            return self.__slot[course.get_classRoom().get_classRoom_id()] == None
        return True

    def change_course(self, course=None, clsR=None):  # 改变某个教室内被放入的课程
        if self.__slot[clsR]:
            if self.__slot[clsR].get_courseNum() > 5 and self.__related_slot:
                self.__related_slot.remove_cls_from_slt_special(self.__slot[clsR])

            self.__slot[clsR] = None
        if course:
            self.__slot[clsR] = course
            if course.get_courseNum() > 5 and self.__related_slot:
                self.__related_slot.add_cls_into_slt_special(course)

    def set_related_slot(self, re):
        self.__related_slot = re

    def get_course(self, clsR):
        return self.__slot[clsR]

    def get_slot_special(self):
        return self.__slot_special

    def remove_cls_from_slt_special(self, course):
        self.__slot_special.remove(course)

    def add_cls_into_slt_special(self, course):
        self.__slot_special.append(course)

class Chromo:
    def __init__(self, math_course = [], course_lst = [], chromosome=None, student_ideal_class=None, total_classRoom_num=None, course_overlap=None, tmp_condition=None):
        self.__count = 0
        random.shuffle(course_lst)
        self.__course_list = course_lst
        self.__cor_dic = [{} for i in range(7)]
        self.__cor_d = {}
        self.__total_classRoom_num = total_classRoom_num
        self.__student_ideal_class = student_ideal_class
        # adapt记录了当前染色体的适应度
        self.__adapt_lst = [{None} for i in range(7)]
        self.__math_course_set = {""}
        for i in math_course:
            self.__math_course_set.add(i)
        self.__adapt = 0
        self.__all_course_can = 0
        self.__chromosome = [Slot(total_classRoom_num=total_classRoom_num) for i in range(7)]
        # slot1、2里面放置课时数量>5的课程的5个课时，多余出来的课时统一放在slot6里面
        self.__chromosome[0].set_related_slot(self.__chromosome[5])
        self.__chromosome[1].set_related_slot(self.__chromosome[5])
        # slot3,4里面放置课时>5的课程多余出来的课时统一放在slot7里面
        self.__chromosome[2].set_related_slot(self.__chromosome[6])
        self.__chromosome[3].set_related_slot(self.__chromosome[6])
        # slot5里面不放置课时数量大于5节的课程
        # slot6,7里面放置课时数量>5的课程多余出来的课时
        self.__is_good = True  # 判断这个染色体有没有创建成功
        # 然后按顺序将课程放进染色体，c_index记录了当前的课程的索引
        c_index = 0
        course_lst_len = len(course_lst)
        # current_slot 记录了当前判断的slot索引
        # 按顺序从0～6
        if chromosome == None:
            if tmp_condition == None:
                tmp_condition = random.randint(0, 2)
            if tmp_condition == 0:
                current_slot = 0
                while c_index < course_lst_len:
                    # 记录当前课程, current_slot记录了当前判断的slot
                    if course_lst[c_index].get_courseNum() > 5:
                        if self.__chromosome[current_slot].class_canput(course_lst[c_index]):
                            self.__chromosome[current_slot].change_course(course_lst[c_index], course_lst[
                                c_index].get_classRoom().get_classRoom_id())
                            c_index += 1
                            current_slot = 0
                        else:
                            current_slot += 1
                        # 证明当前课程没办法放到染色体中，所以可以宣布推出染色体进行重新创建
                        if current_slot == 7:
                            self.__is_good = False
                            break
                    else:
                        c_index += 1

                if self.__is_good:
                    tmp_course_overlap = {}
                    course_overlap_copy = {}
                    for c in course_overlap:
                        course_overlap_copy[c] = course_overlap[c].copy()

                    for c in course_overlap_copy:
                        tmp_course_overlap[c] = set()
                        i = 0
                        target = random.randint(1, 3)
                        while i != target and course_overlap_copy[c]:
                            tmp_max_c = max(course_overlap_copy[c].items(), key=lambda x: x[1])[0]
                            course_overlap_copy[c].__delitem__(tmp_max_c)
                            tmp_course_overlap[c].add(tmp_max_c)
                            i += 1

                            if course_overlap_copy[c] == {}:
                                break

                        course_overlap_copy = tmp_course_overlap

                    tmp_slt_course = [set() for i in range(7)]
                    random.shuffle(self.__course_list)
                    for index in range(len(course_lst)):
                        tmp_c = self.__course_list[index]
                        slot = [i for i in range(7)]
                        can_put = False
                        if tmp_c.get_courseNum() == 5:
                            random.shuffle(slot)
                            for each_slt in range(7):
                                if tmp_c.get_course_name() in course_overlap_copy.keys():
                                    if not tmp_slt_course[each_slt].isdisjoint(course_overlap_copy[tmp_c.get_course_name()]):
                                        slot.remove(each_slt)
                                        slot.append(each_slt)

                            for slt in slot:
                                if self.__chromosome[slt].class_canput(tmp_c):
                                    self.__chromosome[slt].change_course(tmp_c, tmp_c.get_classRoom().get_classRoom_id())
                                    tmp_slt_course[slt].add(tmp_c.get_course_name())
                                    can_put = True
                                    break

                        if can_put == False:
                            self.__is_good = False
                            break
            elif tmp_condition == 1:
                slot = [i for i in range(7)]
                while c_index < course_lst_len:
                    # 记录当前课程, current_slot记录了当前判断的slot
                    current_slot = random.choice(slot)
                    slot.remove(current_slot)
                    if self.__chromosome[current_slot].class_canput(course_lst[c_index]):
                        self.__chromosome[current_slot].change_course(course_lst[c_index], course_lst[
                            c_index].get_classRoom().get_classRoom_id())
                        slot = [i for i in range(7)]
                        c_index += 1
                    # 证明当前课程没办法放到染色体中，所以可以宣布推出染色体进行重新创建
                    if not slot:
                        self.__is_good = False
                        break
            else:
                current_slot = 0
                while c_index < course_lst_len:
                    # 记录当前课程, current_slot记录了当前判断的slot
                    if course_lst[c_index].get_courseNum() > 5:
                        if self.__chromosome[current_slot].class_canput(course_lst[c_index]):
                            self.__chromosome[current_slot].change_course(course_lst[c_index], course_lst[
                                c_index].get_classRoom().get_classRoom_id())
                            c_index += 1
                            current_slot = 0
                        else:
                            current_slot += 1
                        # 证明当前课程没办法放到染色体中，所以可以宣布推出染色体进行重新创建
                        if current_slot == 7:
                            self.__is_good = False
                            break
                    else:
                        c_index += 1

                for index in range(len(course_lst)):
                    tmp_c = self.__course_list[index]
                    slot = [i for i in range(7)]
                    can_put = False
                    if tmp_c.get_courseNum() == 5:
                        random.shuffle(slot)

                        for slt in slot:
                            if self.__chromosome[slt].class_canput(tmp_c):
                                self.__chromosome[slt].change_course(tmp_c, tmp_c.get_classRoom().get_classRoom_id())
                                can_put = True
                                break

                        if can_put == False:
                            self.__is_good = False
                            break

            if self.__is_good:
                self.__all_course_can = 0
                self.upgrade_calculate_adapt()
        else:
            for slt in range(7):
                for j in range(total_classRoom_num):
                    self.__chromosome[slt].change_course(chromosome[slt].get_course(j), j)

    def get_chromosome(self):
        return self.__chromosome

    def get_isG(self):
        return self.__is_good

    def get_self_adapt(self):
        return self.__adapt

    def get_self_all(self):
        return self.__all_course_can

    # 传入交换的课程对象，这样这个染色体对自己进行改变，然后交换成功后返回True
    def dot_exchange(self, switch_indexs, other_chromosome, put_slts=None):
        if put_slts == None:
            put_slts = [slt for slt, cor_index in switch_indexs]
        tmp_chromosome = [Slot(total_classRoom_num=self.__total_classRoom_num) for i in range(7)]
        tmp_chromosome[0].set_related_slot(tmp_chromosome[5])
        tmp_chromosome[1].set_related_slot(tmp_chromosome[5])
        tmp_chromosome[2].set_related_slot(tmp_chromosome[6])
        tmp_chromosome[3].set_related_slot(tmp_chromosome[6])
        for slt in range(7):
            for cor_index in range(self.__total_classRoom_num):
                tmp_chromosome[slt].change_course(self.__chromosome[slt].get_course(cor_index), cor_index)

        need_change = []
        # 把所有交换位置上的元素
        # 清空, 重复的课程删除, 交换课程放进来
        for slt, cor_index in switch_indexs:
            switch_c = other_chromosome.get_chromosome()[slt].get_course(cor_index)

            if switch_c:
                for i in self.__chromosome:
                    if i.get_course(cor_index) == switch_c:
                        i.change_course(None, cor_index)
                        break

        for [slt, cor_index], slt1 in zip(switch_indexs, put_slts):
            switch_c = other_chromosome.get_chromosome()[slt].get_course(cor_index)
            tmp_c = self.__chromosome[slt1].get_course(cor_index)
            if tmp_c:
                need_change.append(tmp_c)
            self.__chromosome[slt1].change_course(switch_c, cor_index)

        for i in range(len(switch_indexs)):
            switch_indexs[i][0] = put_slts[i]
        # 把有问题的课程移除
        slt_num = 0
        for slt in self.__chromosome:
            for cor_index in range(self.__total_classRoom_num):
                tmp_c = slt.get_course(cor_index)
                if tmp_c and [slt_num, cor_index] not in switch_indexs:
                    slt.change_course(None, cor_index)
                    if slt.class_canput(tmp_c):
                        slt.change_course(tmp_c, cor_index)
                    else:
                        need_change.append(tmp_c)
            slt_num += 1

        self.__result = None
        self.put_course_back_track(need_change)

        re = False
        if self.__result:
            re = self.check_is_ok()

        if re == False:
            self.__chromosome = tmp_chromosome[:]
            tmp_chromosome = []
        return self.__result and re

    #随机寻找两个不同时段的课程交换
    def mutation(self):
        cor_index = random.choice(range(0, self.__total_classRoom_num))
        slt = random.sample(range(7), k=2)

        cor1 = self.__chromosome[slt[0]].get_course(cor_index)
        cor2 = self.__chromosome[slt[1]].get_course(cor_index)
        self.__chromosome[slt[0]].change_course(None, cor_index)
        self.__chromosome[slt[1]].change_course(None, cor_index)

        if self.__chromosome[slt[1]].class_canput(cor1):
            self.__chromosome[slt[1]].change_course(cor1, cor_index)
        else:
            self.__chromosome[slt[0]].change_course(cor1, cor_index)
            self.__chromosome[slt[1]].change_course(cor2, cor_index)
            return False

        if self.__chromosome[slt[0]].class_canput(cor2):
            self.__chromosome[slt[0]].change_course(cor2, cor_index)
        else:
            self.__chromosome[slt[0]].change_course(cor1, cor_index)
            self.__chromosome[slt[1]].change_course(cor2, cor_index)
            return False

        return True

    #生成染色体里面课程贡献度最高的区间
    def generate_exchange(self, num):
        max_cor = []
        # 去到染色体里面贡献度最高的课程
        max_cor.extend(self.find_max_sum_subdict(self.__cor_d, num))
        max_cor = [max_cor[0], max_cor[-1]]
        switch_index = []
        slt = 0
        cor_index = 0
        while self.__chromosome[slt].get_course(cor_index) != max_cor[0]:
            cor_index += 1
            if cor_index == self.__total_classRoom_num:
                slt += 1
                cor_index = 0
                if slt == 7:
                    slt = 0

        switch_index.append([slt, cor_index])
        while self.__chromosome[slt].get_course(cor_index) != max_cor[1]:
            cor_index += 1
            if cor_index == self.__total_classRoom_num:
                slt += 1
                cor_index = 0
                if slt == 7:
                    slt = 0
            switch_index.append([slt, cor_index])

        return switch_index

    def find_max_sum_subdict(self, d, sub_len=None):
        # 边界检查：字典长度不足目标长度时，无法找到结果
        if len(d) < sub_len:
            return []

        # 核心步骤1：按字典顺序提取键列表和值列表（Python 3.7+字典保持插入顺序）
        keys = list(d.keys())
        values = list(d.values())

        # 核心步骤2：滑动窗口计算值的最大和及对应索引
        # 计算第一个窗口的和（前sub_len个值的和）
        current_sum = sum(values[:sub_len])
        max_sum = current_sum
        max_start = 0  # 记录最大和子区间的起始索引

        # 滑动窗口：从第sub_len个元素开始，右移窗口更新和
        for i in range(sub_len, len(values)):
            # 滑动窗口核心计算：旧窗口和 - 左边界旧值 + 右边界新值
            current_sum = current_sum - values[i - sub_len] + values[i]
            # 若当前和更大，更新最大和及起始索引
            if current_sum > max_sum:
                max_sum = current_sum
                max_start = i - sub_len + 1  # 更新起始索引为当前窗口的左边界

        # 核心步骤3：根据起始索引提取对应的键
        return keys[max_start: max_start + sub_len]

    def find_min_sum_subdict(self, d, sub_len=None):
        # 边界检查：字典长度不足目标长度时，无法找到结果
        if len(d) < sub_len:
            return []

        # 核心步骤1：按字典顺序提取键列表和值列表（Python 3.7+字典保持插入顺序）
        keys = list(d.keys())
        values = list(d.values())

        # 核心步骤2：滑动窗口计算值的最大和及对应索引
        # 计算第一个窗口的和（前sub_len个值的和）
        current_sum = sum(values[:sub_len])
        min_sum = current_sum
        min_start = 0  # 记录最大和子区间的起始索引

        # 滑动窗口：从第sub_len个元素开始，右移窗口更新和
        for i in range(sub_len, len(values)):
            # 滑动窗口核心计算：旧窗口和 - 左边界旧值 + 右边界新值
            current_sum = current_sum - values[i - sub_len] + values[i]
            # 若当前和更小，更新最小和及起始索引
            if current_sum < min_sum:
                min_sum = current_sum
                min_start = i - sub_len + 1  # 更新起始索引为当前窗口的左边界

        # 核心步骤3：根据起始索引提取对应的键
        return keys[min_start: min_start + sub_len]

    # 通过将本染色体里面所有贡献度较低的课程移除然后重新放回染色体
    def upgrade(self, left):
        tmp_chromosome = [Slot(total_classRoom_num=self.__total_classRoom_num) for i in range(7)]
        tmp_chromosome[0].set_related_slot(tmp_chromosome[5])
        tmp_chromosome[1].set_related_slot(tmp_chromosome[5])
        tmp_chromosome[2].set_related_slot(tmp_chromosome[6])
        tmp_chromosome[3].set_related_slot(tmp_chromosome[6])
        for slt in range(7):
            for cor_index in range(self.__total_classRoom_num):
                tmp_chromosome[slt].change_course(self.__chromosome[slt].get_course(cor_index), cor_index)

        if self.__cor_d == {}:
            self.upgrade_calculate_adapt()

        min_cor = []
        min_cor.extend(heapq.nsmallest(random.randint(left, left*2), self.__cor_d, key=lambda k: self.__cor_d[k]))
        while len(min_cor) > left:
            tmp_value = random.choice(min_cor)
            min_cor.remove(tmp_value)

        for slt in self.__chromosome:
            for cor_index in range(self.__total_classRoom_num):
                if slt.get_course(cor_index) in min_cor:
                    slt.change_course(None, cor_index)

        self.__result = None
        self.__count = 0
        random.shuffle(min_cor)
        self.put_course_back_track(min_cor, 1000)

        re = False
        if self.__result:
            re = self.check_is_ok()

        if re == False:
            self.__chromosome = tmp_chromosome[:]
            tmp_chromosome = []
        else:
            self.__cor_d = {}
        return self.__result and re

    def big_change(self):
        tmp_chromosome = [Slot(total_classRoom_num=self.__total_classRoom_num) for i in range(7)]
        tmp_chromosome[0].set_related_slot(tmp_chromosome[5])
        tmp_chromosome[1].set_related_slot(tmp_chromosome[5])
        tmp_chromosome[2].set_related_slot(tmp_chromosome[6])
        tmp_chromosome[3].set_related_slot(tmp_chromosome[6])
        for slt in range(7):
            for cor_index in range(self.__total_classRoom_num):
                tmp_chromosome[slt].change_course(self.__chromosome[slt].get_course(cor_index), cor_index)

        need_change = []
        switch_index = [[i for i in range(self.__total_classRoom_num)] for j in range(7)]
        switch_indexs = []
        for slt in range(7):
            for cor_index in range(self.__total_classRoom_num):
                if self.__chromosome[slt].get_course(cor_index) == None:
                    switch_index[slt].remove(cor_index)

        time = 0
        switch_num = random.randint(15, 35)
        while time < switch_num:
            tmp = random.randint(0, 6)
            if switch_index[tmp]:
                cor_num = random.choice(switch_index[tmp])
                switch_index[tmp].remove(cor_num)
                switch_indexs.append([tmp, cor_num])
                time += 1

        for slt, cor_index in switch_indexs:
            tmp_c = self.__chromosome[slt].get_course(cor_index)
            if tmp_c:
                need_change.append(tmp_c)
                self.__chromosome[slt].change_course(None, cor_index)

        self.__count = 0
        self.__result = None
        random.shuffle(need_change)
        self.put_course_back_track(need_change)

        re = False
        if self.__result:
            re = self.check_is_ok()

        if re == False:
            self.__chromosome = tmp_chromosome[:]
            tmp_chromosome = []
        return self.__result and re

    def upgrade_calculate_adapt(self):
        # 生成染色体中每个时段中包含的课程名称
        self.__adapt_lst = [{""} for i in range(7)]
        self.__cor_dic = [{} for i in range(7)]
        self.__final_one_course = []
        self.__max_one_course = []
        for slt in range(7):
            for cor in self.__chromosome[slt].get_slot():
                if cor:
                    self.__adapt_lst[slt].add(cor.get_course_name())
                    self.__cor_dic[slt][cor.get_course_name()] = 0
        self.__one_course_max = 0
        self.__all_course_can = 0
        total = 0
        # 一个一个的求学生的满意度，然后求和
        for one_student in self.__student_ideal_class.keys():
            one_course = self.__student_ideal_class[one_student]
            self.__must = set(one_course[:3])
            # 通过判断学生能不能选上一套完整的课表来控制self.__is_ok的值
            # 记录了是否结束当前满意度计算，True是继续，False是结束
            self.__is_ok = True
            # 记录了数学和中外教英语课
            # 用self是为了可以在calculate_one_adapt函数里面用
            self.upgrade_calculate_one_adapt(set(one_course))
            self.__final_one_course = []
            for slt, cor in self.__max_one_course:
                if cor in self.__cor_dic[slt]:
                    self.__cor_dic[slt][cor] += 1
            self.__max_one_course = []
            total += self.__one_course_max
            self.__one_course_max = 0
        self.__adapt = total

        for slt in range(7):
            for cor in self.__chromosome[slt].get_slot():
                if cor and cor.get_course_name() in self.__cor_dic[slt].keys():
                    self.__cor_d[cor] = self.__cor_dic[slt][cor.get_course_name()]

    def upgrade_calculate_one_adapt(self, course_lst=None, avoid=None, slt_num=0, result=0):
        if self.__is_ok:
            if slt_num != 7:
                if avoid != slt_num:
                    for one_c in course_lst:
                        if one_c in self.__adapt_lst[slt_num]:
                            if one_c in self.__math_course_set:
                                tmp_course_lst = course_lst.copy()
                                tmp_course_lst.discard(one_c)
                                self.__final_one_course.append([slt_num, one_c])
                                if slt_num == 1 or slt_num == 0:
                                    self.upgrade_calculate_one_adapt(tmp_course_lst, 5, slt_num + 1, result + 1)
                                else:
                                    self.upgrade_calculate_one_adapt(tmp_course_lst, 6, slt_num + 1, result + 1)
                                self.__final_one_course.pop()
                            else:
                                tmp_course_lst = course_lst.copy()
                                tmp_course_lst.discard(one_c)
                                self.__final_one_course.append([slt_num, one_c])
                                self.upgrade_calculate_one_adapt(tmp_course_lst, avoid, slt_num + 1, result + 1)
                                self.__final_one_course.pop()
                self.upgrade_calculate_one_adapt(course_lst, avoid, slt_num + 1, result)
            else:
                if self.__must.isdisjoint(course_lst):
                    if result > self.__one_course_max:
                        self.__one_course_max = result
                        self.__max_one_course = self.__final_one_course[:]
                    if result == 6 or not course_lst:
                        self.__all_course_can += 1
                        self.__is_ok = False

    def put_course_back_track(self, need, limit=1000):
        if self.__result != None:
            return self.__result
        if need:
            slt = [i for i in range(7)]
            for i in range(7):
                slt_num = random.choice(slt)
                slt.remove(slt_num)
                if self.__chromosome[slt_num].class_canput(need[0]):
                    self.__chromosome[slt_num].change_course(need[0], need[0].get_classRoom().get_classRoom_id())
                    self.put_course_back_track(need[1:])
                    self.__count += 1
                    if self.__count > limit:
                        self.__count = 0
                        self.__result = False
                    if self.__result != None:
                        return self.__result
                    self.__chromosome[slt_num].change_course(None, need[0].get_classRoom().get_classRoom_id())
        else:
            self.__count = 0
            self.__result = True

    def check_is_ok(self):
        cor_num = 0
        cor_lst = []
        for slt in self.__chromosome:
            for cor_index in range(self.__total_classRoom_num):
                tmp_c = slt.get_course(cor_index)
                if tmp_c:
                    cor_num += 1
                    slt.change_course(None, cor_index)
                    if slt.class_canput(tmp_c):
                        slt.change_course(tmp_c, cor_index)
                    else:
                        return False
                    cor_lst.append(tmp_c.get_course_name())

        c_lst = []
        for j in self.__course_list:
            c_lst.append(j.get_course_name())

        return cor_num == len(self.__course_list) and Counter(c_lst) == Counter(cor_lst)

    def get_cor_d(self):
        return self.__cor_d

    def generate_self_exchange(self, switch_indexs):
        worst_switch = 0
        min_contribution = 1000
        for time in range(7):
            tmp_contribution = 0
            for slt, cor_index in switch_indexs:
                tmp_c = self.__chromosome[(time + slt) % 7].get_course(cor_index)
                if tmp_c:
                    tmp_contribution += self.__cor_d[tmp_c]

            if tmp_contribution < min_contribution:
                worst_switch = time
                min_contribution = tmp_contribution

        return [(slt + worst_switch) % 7 for slt, cor_index in switch_indexs]

def evolve(math_course, popu, switch_probability, mutate_probability,
    total_classRoom_num, course, student_ideal_class, course_overlap):
        kids_population = []
        popu_size = len(popu)
        weight = [i for i in range(popu_size, 0, -1)]
        must = []
        while popu_size > len(kids_population):
            parents = [0, 0]
            parents[0] = random.choices(popu[:popu_size//4], weights=weight[:popu_size//4])[0]
            parents[1] = random.choices(popu, weights=weight, k=1)[0]
            num = random.randint(5,10)
            num1 = random.randint(10,15)
            if abs(parents[0][1] - parents[-1][1]) > 20:
                num = random.randint(1, 5)
                num1 = random.randint(1, 10)
            if switch_probability > random.uniform(0, 1):
                swi_to1 = parents[1][0].generate_exchange(num)
                swi_to2 = parents[0][0].generate_exchange(num)

                # worst1 = parents[0][0].generate_self_exchange(swi_to1)
                # worst2 = parents[1][0].generate_self_exchange(swi_to2)

                worst1 = None
                worst2 = None
                if switch_probability < random.uniform(0, 1):
                    worst1 = parents[0][0].generate_self_exchange(swi_to1)
                    worst2 = parents[1][0].generate_self_exchange(swi_to2)

                kid2 = Chromo(math_course, course, student_ideal_class=student_ideal_class,
                              total_classRoom_num=total_classRoom_num, chromosome=parents[1][0].get_chromosome())

                if kid2.dot_exchange(swi_to2, parents[0][0], worst2):
                    kids_population.append([kid2, 0, 0])

                kid1 = Chromo(math_course, course, student_ideal_class=student_ideal_class,
                              total_classRoom_num=total_classRoom_num, chromosome=parents[0][0].get_chromosome())

                if kid1.dot_exchange(swi_to1, parents[1][0], worst1):
                    kids_population.append([kid1, 0, 0])
            else:
                switch_index = []
                switch_start = random.randint(0, total_classRoom_num - 1)
                switch_slt = random.randint(0, 6)

                for i in range(num1):
                    switch_index.append([switch_slt, switch_start])
                    switch_start += 1
                    if switch_start == total_classRoom_num:
                        switch_start = 0
                        switch_slt += 1
                        if switch_slt == 7:
                            switch_slt = 0

                kid1 = Chromo(math_course, course, student_ideal_class=student_ideal_class,
                         total_classRoom_num=total_classRoom_num, chromosome=parents[0][0].get_chromosome())
                kid2 = Chromo(math_course, course, student_ideal_class=student_ideal_class,
                         total_classRoom_num=total_classRoom_num, chromosome=parents[1][0].get_chromosome())

                if kid1.dot_exchange(switch_index, parents[1][0]):
                    kids_population.append([kid1, 0, 0])

                if kid2.dot_exchange(switch_index, parents[0][0]):
                    kids_population.append([kid2, 0, 0])

            if abs(parents[0][1] - parents[-1][1]) > 15:
                num1 = random.randint(5, 10)
                if random.randint(0, 2) == 0:
                    num1 = random.randint(10, 15)
                switch_indexs = [[i for i in range(total_classRoom_num)] for _ in range(7)]
                switch_index = []

                while num1 > 0:
                    tmp_slt = random.randint(0, 6)
                    if switch_indexs[tmp_slt]:
                        tmp_cls = random.choice(switch_indexs[tmp_slt])
                        switch_indexs[tmp_slt].remove(tmp_cls)
                        switch_index.append([tmp_slt, tmp_cls])
                        num1 -= 1

                kid2 = Chromo(math_course, course, student_ideal_class=student_ideal_class,
                              total_classRoom_num=total_classRoom_num, chromosome=parents[1][0].get_chromosome())

                if kid2.dot_exchange(switch_index, parents[0][0]):
                    kids_population.append([kid2, 0, 0])

                kid1 = Chromo(math_course, course, student_ideal_class=student_ideal_class,
                              total_classRoom_num=total_classRoom_num, chromosome=parents[0][0].get_chromosome())

                if kid1.dot_exchange(switch_index, parents[1][0]):
                    kids_population.append([kid1, 0, 0])

        for kid_index in range(len(kids_population)):
            tmp = kids_population[kid_index][0]
            kid = Chromo(math_course, course, student_ideal_class=student_ideal_class,
                         total_classRoom_num=total_classRoom_num, chromosome=tmp.get_chromosome())

            if random.uniform(0, 1) < mutate_probability:
                while True:
                    if kid.mutation():
                        break

                if -3 < (popu[0][1] - popu[-1][1]) < 3:
                    tmp_kid = Chromo(math_course, course, student_ideal_class=student_ideal_class,
                             total_classRoom_num=total_classRoom_num, chromosome=kid.get_chromosome())

                    if random.randint(0, 1) == 0:
                        if kid.big_change():
                            kid.upgrade_calculate_adapt()
                            must.append([kid, kid.get_self_all(), kid.get_self_adapt()])
                    else:
                        repeat = 0
                        while True:
                            left = random.randint(15, 30)
                            if kid.upgrade(left):
                                kid.upgrade_calculate_adapt()
                                must.append([kid, kid.get_self_all(), kid.get_self_adapt()])
                                break
                            repeat += 1
                            if repeat > 5:
                                break

                    left = random.randint(3, 10)
                    if tmp_kid.upgrade(left):
                        kids_population[kid_index] = [tmp_kid, 0, 0]
                else:
                    left = random.randint(1, 5)
                    repeat = 0
                    while True:
                        if kid.upgrade(left):
                            break
                        repeat += 1
                        if repeat > 5:
                            break
                    kids_population[kid_index] = [kid, 0, 0]

        if -3 < (popu[0][1] - popu[-1][1]) < 3:
            i = 0
            temp = Chromo(math_course, course, student_ideal_class=student_ideal_class,
                          total_classRoom_num=total_classRoom_num ,course_overlap=course_overlap, tmp_condition=2)
            while i != popu_size // 4:
                if temp.get_isG():
                    i += 1
                    must.append([temp, temp.get_self_all(), temp.get_self_adapt()])
                temp = Chromo(math_course, course, student_ideal_class=student_ideal_class,
                              total_classRoom_num=total_classRoom_num, course_overlap=course_overlap, tmp_condition=2)

        for index in range(5, popu_size - 5):
            if random.uniform(0, 1) > mutate_probability:
                if random.randint(0, 1) == 0:
                    popu[index][0].mutation()
                else:
                    repeat = 0
                    left = random.randint(1, 3)
                    if -3 < (popu[0][1] - popu[-1][1]) < 3:
                        left = random.randint(5, 10)
                    while repeat < 5:
                        if popu[index][0].upgrade(left):
                            break
                        left = random.randint(1, 3)
                        if -3 < (popu[0][1] - popu[-1][1]) < 3:
                            left = random.randint(5, 10)
                        repeat += 1

        kids_population += popu
        for i in range(len(kids_population)):
            kid = kids_population[i][0]
            kid.upgrade_calculate_adapt()
            kids_population[i] = [kid, kid.get_self_all(), kid.get_self_adapt()]

        kids_population.sort(key=lambda x: x[1], reverse=True)
        if must:
            random.shuffle(must)
            if len(must) > popu_size*4//5:
                return kids_population[:popu_size//5] + must[:popu_size*4//5]
            return kids_population[:popu_size - len(must)] + must
        return kids_population[:popu_size]

def one_evolution(math_course, course, student_ideal_class, total_classRoom_num,
    each_generation_value, each_generation_time, course_overlap, each_max_generation, progress_value=None):
        population_size = 100
        # 交换、突变率
        s_switch_probability = 0.6
        e_switch_probability = 0.4
        cur_switch_probability = s_switch_probability

        # 开始和最终的突变率
        s_mutate_probability = 0.3
        e_mutate_probability = 0.8
        cur_mutate_probability = s_mutate_probability

        population = []
        temp = Chromo(math_course, course, student_ideal_class=student_ideal_class, total_classRoom_num=total_classRoom_num
                      , course_overlap=course_overlap)
        i = 0
        record = []
        each_time = []
        while i != population_size:
            if temp.get_isG():
                i += 1
                population.append([temp, temp.get_self_all(), temp.get_self_adapt()])
            temp = Chromo(math_course, course, student_ideal_class=student_ideal_class, total_classRoom_num=total_classRoom_num
                          , course_overlap=course_overlap)

        repeat_time = 0
        population.sort(key=lambda x: (x[1], x[2]), reverse=True)

        same = 0
        evolve_time = 2000
        pre = 0
        while same < 100 and repeat_time < evolve_time and population[0][1] != len(student_ideal_class):
            current_progress = population[0][1] / len(student_ideal_class)
            record.append(current_progress)
            if progress_value is not None and current_progress > progress_value.value:
                progress_value.value = current_progress
            # 先进行交换，再进行突变
            s = time.time()
            population = evolve(math_course, population, cur_switch_probability, cur_mutate_probability, total_classRoom_num,
                                student_ideal_class=student_ideal_class, course=course, course_overlap=course_overlap)
            e = time.time()
            each_time.append(e - s)
            repeat_time += 1
            if pre == population[0][1]:
                same += 1
            else:
                pre = population[0][1]
                same = 0
            if repeat_time < 250:
                cur_mutate_probability = (s_mutate_probability - (s_mutate_probability - e_mutate_probability) * (repeat_time / 250))
                cur_switch_probability = (s_switch_probability - (s_switch_probability - e_switch_probability) * (repeat_time / 250))

            # print(repeat_time, population[0][1] / len(student_ideal_class), population[-1][1]/len(student_ideal_class))
        each_generation_value.append(record)
        each_generation_time.append(each_time)
        each_max_generation.append(population[0])

def runAutomaticSchedulingForAse(config, task=None):
    if config is not None:
        # 教室的名字
        classRoom = [
            "California", "Nevada", "Ohio",
            "Minnesota", "Utah", "Florida",
            "Kansas", "Arizona", "Texas",
            "Georgia", "Colorado", "Oregon",
            "Louisiana", "Michigan", "Maryland",
            "Pennsylvania", "Hawaii", "Rhode Island"
        ]
        # 键是老师的id，值是老师的信息
        teachers_info = {}
        # 课程信息:包含课程名字、老师ID，教室索引、课时数量
        course = []
        math_course = []
        # 学生想要上的课程列表，用于计算适应度
        student_ideal_class = {}

        def value_initial():
            wb = openpyxl.load_workbook("/Users/bdm/Desktop/ase课程信息.xlsx")
            wb = openpyxl.load_workbook("/Users/bdm/Desktop/ase导入文件-真实数据.xlsx")
            course_sheet = wb["非数学课"]
            """----------------------------处理老师和课程信息-------------------------------"""
            row_index = 2
            id_num = 0
            tmp_value = course_sheet.cell(row=row_index, column=2).value
            while tmp_value:
                tmp_course_name = course_sheet.cell(row=row_index, column=1).value.replace('\xa0', " ")
                tmp_cls_num = int(course_sheet.cell(row=row_index, column=3).value)
                if tmp_value not in teachers_info.values():
                    teachers_info[id_num] = tmp_value
                    id_num += 1
                for i in range(tmp_cls_num):
                    course.append([tmp_course_name, list(teachers_info.values()).index(tmp_value), 0, 5])
                row_index += 1
                tmp_value = course_sheet.cell(row=row_index, column=2).value

            course_sheet = wb["数学课"]
            row_index = 2
            tmp_value = course_sheet.cell(row=row_index, column=2).value
            while tmp_value:
                tmp_course_name = course_sheet.cell(row=row_index, column=1).value.replace('\xa0', " ")
                tmp_cls_num = course_sheet.cell(row=row_index, column=3).value
                if tmp_value not in teachers_info.values():
                    teachers_info[id_num] = tmp_value
                    id_num += 1
                for i in range(tmp_cls_num):
                    course.append([tmp_course_name, list(teachers_info.values()).index(tmp_value), 0, 7])
                row_index += 1
                tmp_value = course_sheet.cell(row=row_index, column=2).value

            """----------------------------处理学生想选的课程-------------------------------"""

            row_index = 2
            course_sheet = wb["选课"]
            while course_sheet.cell(row=row_index, column=1).value:
                one_student_cls = []
                for i in range(2, 10):
                    if course_sheet.cell(row=row_index, column=i).value:
                        one_student_cls.append(course_sheet.cell(row=row_index, column=i).value.replace("\xa0", " "))

                student_ideal_class[course_sheet.cell(row=row_index, column=1).value] = one_student_cls
                row_index += 1

        # value_initial()
        id = 0
        for teacher in config["非数学课设置"] + config["数学课设置"]:
            if teacher["老师名称"] not in teachers_info.values():
                teachers_info[id] = teacher["老师名称"]
                id += 1

        for cls in config["非数学课设置"]:
            for i in range(cls["班级数"]):
                course.append([cls["课程名称"], list(teachers_info.values()).index(cls["老师名称"]), 0, 5])

        for cls in config["数学课设置"]:
            for i in range(cls["班级数"]):
                course.append([cls["课程名称"], list(teachers_info.values()).index(cls["老师名称"]), 0, 7])

        for student in config["学生信息"]:
            tmp = list(student.values())
            del tmp[0]
            student_ideal_class[student["学生姓名"]] = tmp

        course_names = {cls["课程名称"] for cls in config["非数学课设置"] + config["数学课设置"]}
        for student_name, choices in student_ideal_class.items():
            student_ideal_class[student_name] = [
                choice for choice in choices
                if choice and choice != "Nothing" and choice in course_names
            ]

        def calculate_overlap_counts_dict(dict_list):
            """
            计算字典值中的字符串重叠次数

            参数:
                dict_list: 包含多个字典的列表，只考虑字典的值

            返回:
                一个字典，键为字符串，值为另一个字典，
                内部字典的键为其他字符串，值为重叠次数
            """
            overlap_counts = defaultdict(lambda: defaultdict(int))

            for dict_item in dict_list.values():
                # 提取所有值，并统计每个值的出现次数
                value_count = {}
                for value in dict_item:
                    value_count[value] = value_count.get(value, 0) + 1

                # 获取所有唯一值
                unique_values = list(value_count.keys())

                # 对于每个值对，计算共现次数
                for i, val1 in enumerate(unique_values):
                    for j, val2 in enumerate(unique_values):
                        if i < j:  # 避免重复计算和自比较
                            # 共现次数 = val1出现次数 * val2出现次数
                            count = value_count[val1] * value_count[val2]

                            # 记录共现次数（双向记录）
                            overlap_counts[val1][val2] += count
                            overlap_counts[val2][val1] += count

            # 转换为普通字典
            result = {}
            for val1, others in overlap_counts.items():
                result[val1] = dict(others)

            return result

        course_overlap = calculate_overlap_counts_dict(student_ideal_class)
        for i in course_overlap:
            if "Nothing" in course_overlap[i]:
                course_overlap[i].__delitem__("Nothing")

        # 将每个老师定义成对象，覆盖原来的值，键不变
        for i in teachers_info.keys():
            teachers_info[i] = Teacher(n=teachers_info[i], ID=i)
        # 将每个教室定义成对象, 并将原来的值进行覆盖
        for i in range(len(classRoom)):
            classRoom[i] = ClassRoom(n=classRoom[i], ID=i)

        total_classRoom_num = len(classRoom)
        # 当前每个教室一周被放入的课时数量
        cur_classRoom_avai = {i: 0 for i in range(total_classRoom_num)}

        # 帮忙找到当前被放入最少课程的教室索引
        def find_key_with_min_value():
            min_value = 40
            min_key = 0
            for key in cur_classRoom_avai.keys():
                if cur_classRoom_avai[key] < min_value:
                    min_value = cur_classRoom_avai[key]
                    min_key = key
            return min_key

        # 给每个课程分配一个教室
        for i in range(len(course)):
            if course[i][3] > 5:
                tmp_clsRmId = find_key_with_min_value()
                cur_classRoom_avai[tmp_clsRmId] += course[i][3]
                course[i][2] = tmp_clsRmId

        for i in range(len(course)):
            if course[i][3] == 5:
                tmp_clsRmId = find_key_with_min_value()
                cur_classRoom_avai[tmp_clsRmId] += course[i][3]
                course[i][2] = tmp_clsRmId

        # 创建出课程对象，将原来的列表覆盖
        cor_id = 0
        for i in range(len(course)):
            if course[i][3] > 5:
                math_course.append(course[i][0])
            course[i] = Course(teachers_info[course[i][1]], course[i][0], classRoom[course[i][2]], course[i][3], cor_id)
            cor_id += 1

        def show_result(chromosome, file):
            wb = load_workbook(file)
            wb.__delitem__("hello")
            wb.create_sheet("hello", 0)

            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

            course_lst = []
            tea_lst = []

            for slt in chromosome:
                tmp_c = []
                tmp_t = []
                for cor in slt.get_slot():
                    if cor:
                        tmp_c.append(cor.get_course_name())
                        tmp_t.append(cor.get_teacher().get_name())
                    else:
                        tmp_c.append("")
                        tmp_t.append("")

                course_lst.append(tmp_c)
                tea_lst.append(tmp_t)

            row = 2
            col = 3
            for i in range(7):
                for one_cor in range(len(course_lst[0])):
                    wb["hello"].cell(row=row, column=col, value=course_lst[i][one_cor])
                    wb["hello"].cell(row=row + 5, column=col, value=tea_lst[i][one_cor])
                    col += 2
                row += 6
                col = 3

            row = [1, 1]
            col = [3, 3]
            for i in range(len(course_lst[0])):
                wb["hello"].merge_cells(start_row=row[1], start_column=col[1], end_row=row[1], end_column=col[1] + 1)
                for j in range(7):
                    row[1] += 1
                    wb["hello"].merge_cells(start_row=row[1], start_column=col[1], end_row=row[1] + 4,
                                            end_column=col[1] + 1)
                    row[1] += 5
                    wb["hello"].merge_cells(start_row=row[1], start_column=col[1], end_row=row[1],
                                            end_column=col[1] + 1)
                col[0] += 2
                row[1] = row[0]
                col[1] = col[0]

            for i in range(0, 7):
                wb["hello"].cell(2 + i * 6, 1, f"Slot{i + 1}")
                wb["hello"].merge_cells(start_row=2 + i * 6, start_column=1, end_row=2 + i * 6 + 4, end_column=1)

            for row in wb["hello"].iter_rows(1, 43, 1, 2 * (total_classRoom_num + 1)):
                for cell in row:
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text="hello")
                    cell.border = thin_border

            wb.save(file)

        manager = multiprocessing.Manager()
        each_generation_value = manager.list()
        each_generation_time = manager.list()
        each_max_generation = manager.list()
        progress_value = manager.Value('d', 0.0)
        all_process = []
        for times in range(1):
            for i in range(5):
                # 这里为了让args识别我穿进来的参数是变量组，需要加逗号
                p = Process(target=one_evolution, args=(math_course, course, student_ideal_class, total_classRoom_num,
                            each_generation_value, each_generation_time, course_overlap, each_max_generation, progress_value))
                all_process.append(p)
                p.start()
            while any(p.is_alive() for p in all_process):
                if task is not None:
                    task.progress = int(progress_value.value * 100)
                    task.save(update_fields=['progress'])
                time.sleep(1)
            for p in all_process:
                p.join()

        # for each in each_generation_value:
        #     print(each)
        #
        # for each in each_generation_time:
        #     print(each)

        if not each_max_generation:
            raise RuntimeError("ASE scheduling failed: no valid population was produced")

        max_population = max(each_max_generation, key=lambda x:x[1])
        if task is not None:
            task.progress = int(max_population[1] / len(student_ideal_class) * 100)
            task.save(update_fields=['progress'])
        for i in range(len(classRoom)):
            classRoom[i] = classRoom[i].get_name()
        result = [max_population[1] / len(student_ideal_class), [classRoom]]
        for slt in max_population[0].get_chromosome():
            slts = []
            for cls in slt.get_slot():
                if cls:
                    slts.append([cls.get_course_name(), cls.get_teacher().get_name()])
                else:
                    slts.append([])
            result[1].append(slts)

        return result
        # show_result(max_population[0].get_chromosome(), "/Users/bdm/Desktop/output.xlsx")
