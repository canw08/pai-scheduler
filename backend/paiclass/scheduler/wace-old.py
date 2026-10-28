import enum
import random
import copy
import json

# 全局参数 parameter
PopulationSize = 100
Generations = 1000
crossover_rate = 0.8
mutation_rate=0.05


# 课程名字
gCourseNum = 0
COURSE_PHE = "PHE"
#CourseName = enum.Enum("CourseName", ("COMM", "COMP", "ECON", "MATH", "ACCT", "PHY", "English", "IELTS", "PHE", "PSY", "COU"))
# 课程类别（商/理/公共）
CourseType = enum.Enum('CourseType', ('BUS', 'SCI', 'COMMON'))
# 班级类别（有的班级为商理混班，单独标出来B/S的班级就是拆班上课，不在适用行政班级）
ClassID = enum.Enum("ClassID", ("G12_1", "G12_2", "G12_3"))
ClassType = enum.Enum("ClassType", ("BUS", "SCI", "COMBO"))

# 老师名录
NO_NAME = "No Name"
gTeacherDict = {}

schoolDays = 5 # for one week
dayPeriod = 7 # 一天7节课
classNum = 0

gCourseDNAPopulation = []
gAllClassLst = []
gAllCourseLst = []
gPEDay = -1
gPEPeriod = -1

# 课程类
class Course:

    def __init__(self, classID, name, teacher, courseType, totalPeriods, teachingClass):
        self.__ID = classID
        self.__name = name
        self.__teacher = teacher    # 体育课的老师必为空串
        self.__type = courseType
        self.__totalPeriods = totalPeriods
        self.__Count = 0
        self.__teachingClass = teachingClass
        self.__relatedCourse= None # 该课程的关联对开课程课程（暂时仅供商理混班使用）
        self.__needPutTwoTogether = False
        self.__continuePeriodNum = 1 # 期望连堂数
        self.__oddEvenWeek = None # 单双周轮换课程
        self.__requiredTime = None # 必须要安排的时间

    def getCourseID(self):
        return self.__ID

    def setCourseID(self, classID):
        self.__ID = classID

    def getCourseType(self):
        return self.__type

    def getTotalPeriods(self):
        return self.__totalPeriods

    def getCoursePeriods(self):
        return self.__totalPeriods

    def getTeachingClass(self):
        return self.__teachingClass

    def getName(self):
        return self.__name

    def getTeacher(self):
        return self.__teacher

    def setRelatedCourse(self, relatedCourse):
        self.__relatedCourse = relatedCourse

    def getRelatedCourse(self):
        return self.__relatedCourse

    def setPutTwoTogether(self, putTogether):
        self.__needPutTwoTogether = putTogether

    def getPutTwoTogether(self):
        return self.__needPutTwoTogether

    def increaseCount(self):
        self.__Count += 1

    def getCount(self):
        return self.__Count

    def resetCount(self):
        self.__Count = 0

    def setContinuePeriodNum(self, num):
        self.__continuePeriodNum = num
        return

    def getContinuePeriodNUm(self):
        return self.__continuePeriodNum

    def setRequiredTime(self, requiredTime):
        self.__requiredTime = requiredTime

    def getRequiredTime(self):
        return self.__requiredTime

    def setOddEvenWeek(self, oddEvenWeek):
        self.__oddEvenWeek = oddEvenWeek

    def getOddEvenWeek(self):
        return self.__oddEvenWeek


# 班级类
class G12Class:

    def __init__(self, ID, classType):
        self.__ID = ID
        self.__classType = classType

    def getType(self):
        return self.__classType

    def getID(self):
        return self.__ID

    def setTeacherLst(self, teacherLst):
        self.__teacherLst = teacherLst

    def getTeacherLst(self):
        return self.__teacherLst

    def setCourseLst(self, courseLst):
        self.__courseLst = courseLst

    def getCourseLst(self):
        return self.__courseLst


class Teacher:

    def __init__(self, id, name, department, unsuitable_period):
        self.__id = id
        self.__name = name
        self.__department = department
        self.__unsuitablePeriod = unsuitable_period

    def getID(self):
        return self.__id

    def getName(self):
        return self.__name

    def getUnsuitablePeriod(self):
        return self.__unsuitablePeriod


# for test
def printOneClassSchedule(CSDNA, classID):
    print("------Class%d------"%(classID +1))
    for i in range(schoolDays):
        for j in range(dayPeriod):
            count = i * dayPeriod * classNum + j * classNum + classID
            courseName = CSDNA[count][0].getName()
            if courseName == COURSE_PHE:    # 体育课需要特殊处理
                s = courseName+"_"+"体育老师"
            else:
                s = CSDNA[count][0].getName()+"_"+gTeacherDict[CSDNA[count][0].getTeacher()].getName()
                for k in range(1, len(CSDNA[count])):
                    s += "/"+CSDNA[count][k].getName()+"_"+gTeacherDict[CSDNA[count][k].getTeacher()].getName()
            print("%15s\t\t" %s, end="")
        print()


# 调整，使体育连堂
def ModifyForPE(courseLst, PEDay, PEPeriod):

    posLst = []
    for i in range(len(courseLst)):
        if courseLst[i].getName() == COURSE_PHE and\
                (i != PEDay*dayPeriod+PEPeriod and i != PEDay*dayPeriod+PEPeriod+1):
            posLst.append(i)

    PETargetPos = PEDay*dayPeriod+PEPeriod
    for count in range(len(posLst)):
        # for test
        # print("Before Change:========")
        # print("PHE POS:%d, Name:%s"%(posLst[count], cBAK[posLst[count]].getName()))
        # print("Other POS:%d, Name:%s" % (PEDay*dayPeriod+PEPeriod+count, cBAK[PEDay*dayPeriod+PEPeriod+count].getName()))

        if courseLst[PETargetPos].getName() == COURSE_PHE:
            PETargetPos += 1
        courseLst[posLst[count]], courseLst[PETargetPos] = courseLst[PETargetPos], courseLst[posLst[count]]
        # tmp = courseLst[posLst[count]]
        # courseLst[posLst[count]] = courseLst[PEDay*dayPeriod+PEPeriod+count]
        # courseLst[PEDay * dayPeriod + PEPeriod+count] = tmp

        # # for test
        # print("After Change:========")
        # print("PHE POS:%d, Name:%s" % (
        #     PEDay * dayPeriod + PEPeriod + count, courseLst[PEDay * dayPeriod + PEPeriod + count].getName()))
        # print("Other POS:%d, Name:%s" % (posLst[count], courseLst[posLst[count]].getName()))

    for i in range(len(courseLst)):
        if courseLst[i].getName() == COURSE_PHE:
            if courseLst[i+1].getName() != COURSE_PHE:
                assert 0
            break
    return




# 生成种群
def generateCourseDNAPopulation():
    global gCourseDNAPopulation
    # 基因链DNA按照D1-E1-C1， D1-E1-C2, D1-E1-C3, D1-E2-C1, D1-E2-C2, D1-E2-C3, ----, D5-E7-C1, D5-E7-C2, D5-E7-C3
    # 的顺序存储，其中D表示一周的工作日，E表示一天的课时（一天按照7课时计），C表示班级（C1-C2-C3）
    gCourseDNAPopulation = [[[] for i in range(schoolDays*dayPeriod*classNum)] for i in range(PopulationSize)]

    if gPEDay == -1 or gPEPeriod == -1: # 体育课的必修时间必须已经设置完毕
        assert 0

    for i in range(len(gCourseDNAPopulation)):
        curDNA = gCourseDNAPopulation[i]
        # 注意1，对于行政班2班，商理合班，有些商理课程作为一个固定搭配组合，占用同一课时
        # 注意2，心理和学业咨询是单双周制
        # 注意3，体育课所有班级定在同一个时间段，且不得分开

        clsCount = 0
        for curClass in gAllClassLst:    # 按照班级遍历
            weekCoursesOneClass = []
            if curClass.getType() == ClassType.BUS: # 商科班
                for course in gAllCourseLst:
                    # 当前班过滤掉理科班的课程
                    if course.getCourseType() != CourseType.SCI and course.getTeachingClass().getID()==curClass.getID():
                        needAddThisCourse = True
                        if course.getOddEvenWeek() is not None and course.getOddEvenWeek() in weekCoursesOneClass:
                            needAddThisCourse = False  # 单双周的课只加一个即可
                        if needAddThisCourse:
                            for k in range(course.getCoursePeriods()):
                                weekCoursesOneClass.append(course)  # 按照某班一周的课程生成列表
                random.shuffle(weekCoursesOneClass) # 打乱顺序
                ModifyForPE(weekCoursesOneClass, gPEDay, gPEPeriod)  # 调整，使体育连堂
                for k in range(len(weekCoursesOneClass)): # 将该班一周的课放入完整基因链中
                    curDNA[k*classNum+clsCount].append(weekCoursesOneClass[k])
                    if weekCoursesOneClass[k].getOddEvenWeek() is not None:  # 将单双周的课加入
                        curDNA[k * classNum + clsCount].append(weekCoursesOneClass[k].getOddEvenWeek())
            elif curClass.getType() == ClassType.SCI: # 理科班
                for course in gAllCourseLst:
                    # 当前班过滤掉商科班的课程
                    if course.getCourseType() != CourseType.BUS and course.getTeachingClass().getID()==curClass.getID():
                        needAddThisCourse = True
                        if course.getOddEvenWeek() is not None and course.getOddEvenWeek() in weekCoursesOneClass:
                            needAddThisCourse = False  # 单双周的课只加一个即可
                        if needAddThisCourse:
                            for k in range(course.getCoursePeriods()):
                                weekCoursesOneClass.append(course)  # 按照某班一周的课程生成列表
                random.shuffle(weekCoursesOneClass) # 打乱顺序
                ModifyForPE(weekCoursesOneClass, gPEDay, gPEPeriod)  # 调整，使体育连堂
                for k in range(len(weekCoursesOneClass)): # 将该班一周的课放入完整基因链中
                    curDNA[k*classNum+clsCount].append(weekCoursesOneClass[k])
                    if weekCoursesOneClass[k].getOddEvenWeek() is not None: # 将单双周的课加入
                        curDNA[k*classNum+clsCount].append(weekCoursesOneClass[k].getOddEvenWeek())
            elif curClass.getType() == ClassType.COMBO: # 商理混合
                for course in gAllCourseLst:
                    # 过滤出该班该上的课程，下面判断不等于SCI，是考虑先把COMMON和BUS加入DNA，然后再把对开的SCI课程从BUS的RelatedCourse引入
                    if course.getCourseType() != CourseType.SCI and course.getTeachingClass().getID()==curClass.getID():
                        needAddThisCourse = True
                        if course.getOddEvenWeek() is not None and course.getOddEvenWeek() in weekCoursesOneClass:
                            needAddThisCourse = False # 单双周的课只加一个即可
                        if needAddThisCourse:
                            for k in range(course.getCoursePeriods()):
                                weekCoursesOneClass.append(course) # 按照某班一周的课程生成列表
                random.shuffle(weekCoursesOneClass) # 打乱顺序
                ModifyForPE(weekCoursesOneClass, gPEDay, gPEPeriod)  # 调整，使体育连堂
                for k in range(len(weekCoursesOneClass)): # 将该班一周的课放入完整基因链中
                    curDNA[k*classNum+clsCount].append(weekCoursesOneClass[k])
                    if weekCoursesOneClass[k].getRelatedCourse() is not None:  # 将与商科同时上的理科课加入到DNA中
                        curDNA[k*classNum+clsCount].append(weekCoursesOneClass[k].getRelatedCourse())
                    if weekCoursesOneClass[k].getOddEvenWeek() is not None: # 将单双周的另外一节课加入DNA
                        curDNA[k*classNum+clsCount].append(weekCoursesOneClass[k].getOddEvenWeek())
            clsCount += 1
        #print("=========================================================================================")
    return

# 计算适应度
def computerFitness():
    PUNISH_sameTeacher = 10
    PUNISH_tooMuchCourseInOneDay = 0.3
    PUNISH_tooMuchCourseForTeacher = 0.1
    PUNISH_unsuitableClass = 0.3
    PUNISH_uniformDistribute = 0.01

    fitnessLst = []

    # 计算种群的适应度
    for curDNA in gCourseDNAPopulation:
        score = 0
        # 规则一：查看同一天同一个课时，不同班是否有老师冲突(有一个冲突，加PUNISH_sameTeacher分)
        for i in range(schoolDays*dayPeriod):
            for j in range(classNum-1): # 当前班
                for m in range(len(curDNA[i*classNum+j])): # 可能是混班的课/单双周的课，同时有两节
                    teacher1 = curDNA[i*classNum+j][m].getTeacher()
                    for k in range(j+1, classNum): # 后面的班
                        for n in range(len(curDNA[i * classNum + k])): # 可能是混班的课/单双周的课，同时有两节
                            teacher2 = curDNA[i * classNum + k][n].getTeacher()
                            if teacher1 == teacher2 and teacher1 != "": #NO_NAME: # 不考虑体育课程
                                score += PUNISH_sameTeacher

        # 规则二：同一天同一门课在同一个班不能超过三节(含)(有一个，加PUNISH_tooMuchCourseInOneDay分)
        for i in range(schoolDays):
            for j in range(classNum):
                #dayCourseLst = [0 for k in range(len(CourseName))]
                dayCourseLst = [0 for k in range(gCourseNum)]
                for k in range(dayPeriod):
                    for m in range(len(curDNA[i*dayPeriod*classNum+k*classNum+j])):
                        #print(curDNA[i*dayPeriod*classNum+k*classNum+j][m].getName())
                        dayCourseLst[curDNA[i*dayPeriod*classNum+k*classNum+j][m].getCourseID()] += 1
                for k in dayCourseLst:
                    if k >= 3:
                        score += PUNISH_tooMuchCourseInOneDay

        # 规则三：某个老师不能在某天上午连着上四节（有一个冲突，加PUNISH_tooMuchCourseForTeacher）
        for i in range(schoolDays):
            dayOffset = i*dayPeriod*classNum
            teacherIDLst = []
            for j in range(4): # 上午四节课
                teacherFlagLst = []
                for k in range(classNum):
                    for m in range(len(curDNA[dayOffset+j*classNum+k])):
                        teacherID = curDNA[dayOffset+j*classNum+k][m].getTeacher()
                        if teacherID not in teacherFlagLst: # 同一课时如果有老师有冲突，只记一次
                            teacherIDLst.append(teacherID)
                            teacherFlagLst.append(teacherID)
            flagLst = []
            for j in teacherIDLst:
                if j not in flagLst:
                    flagLst.append(j)
                    if teacherIDLst.count(j) >= 4:
                        score += PUNISH_tooMuchCourseForTeacher

        # 规则四：某些老师不能在某日某个课时排课
        for i in range(schoolDays):
            for j in range(dayPeriod):
                for k in range(classNum):
                    offset = i*dayPeriod*classNum+j*classNum+k
                    for m in range(len(curDNA[offset])):
                        teacher = curDNA[offset][m].getTeacher()
                        if teacher in gTeacherDict and gTeacherDict[teacher].getUnsuitablePeriod() is not None:
                            if [i, j] in gTeacherDict[teacher].getUnsuitablePeriod():
                                score += PUNISH_unsuitableClass

        # 规则五：课程尽量分布均匀，采用课程实际占用天数和课程节数之比的倒数



        # 这里还可以添加规则

        # for test
        # if score == 0:
        #     print("====== for test ======================")
        #     for i in range(3):
        #         printOneClassSchedule(curDNA, i)
        #     print("====== for test end ======================")

        fitnessLst.append(score)

    return fitnessLst


# 排序轮盘赌选择
def rouletteSort_selection(population):
    total = PopulationSize * (1+PopulationSize) // 2
    pick = random.uniform(0, total)
    current = 0
    for i in range(PopulationSize, 0, -1):
        current += i
        if current >= pick:
            return population[PopulationSize-i]


# 部分映射交叉
def pmx_crossover(parent1, parent2):

    child1 = parent1[:]
    child2 = parent2[:]
    # 体育课不参与交叉，
    # 生成每个班的课程基因链，基因为课程的字符串（带标号），去掉体育课，这样基因链长度为33节
    for classID in range(classNum):
        # print("========Parent1========")
        # printOneClassSchedule(parent1, classID)
        # print("========Parent2========")
        # printOneClassSchedule(parent2, classID)
        p1PEIdx = -1
        p2PEIdx = -1
        p1 = []
        p1Idx = []
        for day in range(schoolDays):
            for period in range(dayPeriod):
                offset = day * dayPeriod * classNum + period*classNum + classID
                if parent1[offset][0].getName() == COURSE_PHE:
                    if p1PEIdx == -1:   # 记录体育课是第几节课
                        p1PEIdx = day * dayPeriod + period
                else:
                    p1.append("%s_%d" %(parent1[offset][0].getName(), parent1[offset][0].getCount()))
                    p1Idx.append(day * dayPeriod + period)  # 记录了每一节课在原始DNA中的位置（第几节课）
                    parent1[offset][0].increaseCount() # 标注是某个课程的第几节课，保证该课时在新的数列p1中ID是唯一的
        for course in gAllCourseLst: # 添加完毕，将所有课程的ID重置为0
            course.resetCount()
        # print(p1)
        # print(p1Idx)
        p2 = []
        p2Idx = []
        for day in range(schoolDays):
            for period in range(dayPeriod):
                offset = day * dayPeriod * classNum + period * classNum + classID
                if parent2[offset][0].getName() == COURSE_PHE:
                    if p2PEIdx == -1:   # 记录体育课是第几节课
                        p2PEIdx = day * dayPeriod + period
                else:
                    p2.append("%s_%d" % (parent2[offset][0].getName(), parent2[offset][0].getCount()))
                    p2Idx.append(day * dayPeriod + period) # 记录了每一节课在原始DNA中的位置（第几节课）
                    parent2[offset][0].increaseCount() # 标注是某个课程的第几节课，保证该课时在新的数列p2中ID是唯一的
        for course in gAllCourseLst: # 添加完毕，将所有课程的ID重置为0
            course.resetCount()
        # print(p2)
        # print(p2Idx)

        size = len(p1)
        while True:
            start, end = sorted(random.sample(range(size), 2))
            if end-start+1 >= 5:    # 防止区间过短
                break
        c1, c2 = p1[:], p2[:]

        # print("Before PMX: c1/c2=======================")
        # print(c1)
        # print(c2)
        # print()

        # PMX操作：交换中间段
        for i in range(start, end):
            pos = c1.index(p2[i])
            c1[pos], c1[i] = c1[i], c1[pos]
            p1Idx[i], p1Idx[pos] = p1Idx[pos], p1Idx[i]
            pos = c2.index(p1[i])
            c2[pos], c2[i] = c2[i], c2[pos]
            p2Idx[i], p2Idx[pos] = p2Idx[pos], p2Idx[i]

        # print("After PMX: c1/c2=======================")
        # print(c1)
        # print(c2)
        # print()

        # 在调整后的序列内插入体育课的下标，补齐35节课
        if len(p1Idx) > schoolDays*dayPeriod-2:
            assert 0
        p1Idx.insert(p1PEIdx, p1PEIdx)
        p1Idx.insert(p1PEIdx+1, p1PEIdx+1)
        if len(p2Idx) > schoolDays*dayPeriod-2:
            assert 0
        p2Idx.insert(p2PEIdx, p2PEIdx)
        p2Idx.insert(p2PEIdx+1, p2PEIdx+1)

        for i in range(len(p1Idx)):
            child1[i*classNum+classID] = parent1[p1Idx[i]*classNum+classID]
            # if i == p1PEIdx and child1[i*classNum+classID][0].getName()==CourseName.PHE and\
            #         parent1[p1Idx[i+1]*classNum+classID][0].getName() != CourseName.PHE:
            #     assert 0

        for i in range(len(p2Idx)):
            child2[i*classNum+classID] = parent2[p2Idx[i]*classNum+classID]
            # if i == p2PEIdx and child2[i*classNum+classID][0].getName()==CourseName.PHE and\
            #         parent2[p2Idx[i+1]*classNum+classID][0].getName() != CourseName.PHE:
            #     assert 0

        # print("Start:%d   End:%d"%(start, end))
        # print("========Child1========")
        # printOneClassSchedule(child1, classID)
        # checkCourseSchedule(child1)
        # print("========Child2========")
        # printOneClassSchedule(child2, classID)
        checkCourseSchedule(child2)

    return child1, child2


# 突变函数
def mutate(curDNA, mutation_rate):

    for classID in range(classNum):
        if random.random() < mutation_rate:
            # print("========before mutate========")
            # printOneClassSchedule(curDNA, classID)

            while True:
                i, j = random.sample(range(schoolDays*dayPeriod), 2)
                if curDNA[i*classNum+classID][0].getName() != COURSE_PHE \
                        and curDNA[j * classNum + classID][0].getName() != COURSE_PHE:
                    break   # 体育课不能动，需要重新生成

            curDNA[i*classNum+classID], curDNA[j*classNum+classID] = \
                curDNA[j*classNum+classID], curDNA[i*classNum+classID]

            # print("Start:%d   End:%d" % (i, j))
            # print("========after mutate========")
            # printOneClassSchedule(curDNA, classID)
    return curDNA

# 检测新的课表是否合法
def checkCourseSchedule(curDNA):
    for course in gAllCourseLst:  # 添加完毕，将所有课程的ID重置为0
        course.resetCount()

    for classID in range(classNum):
        for i in range(schoolDays * dayPeriod):
            offset = i*classNum + classID
            for m in range(len(curDNA[offset])):
                curCourse = curDNA[offset][m]
                curCourse.increaseCount()
                if curCourse.getCount() > curCourse.getTotalPeriods():
                    assert 0

    for course in gAllCourseLst:  # 添加完毕，将所有课程的ID重置为0
        course.resetCount()


# 解析json格式，并生成对应的数据结构
def parseScheduleJson(jsonStr):
    data = jsonStr
    # data = json.loads(jsonStr)

    # 老师信息
    for teacher in data.get("teachers", []):

        # 必须同时满足两个条件才记录
        if "name" not in teacher:
            assert 0

        unsuitableParam = None
        if "unsuitable_period" in teacher:       # 生成老师不能排课时段的字典
            unsuitableParam = [list(p) for p in teacher["unsuitable_period"]]

        # 构建教师ID到教师对象的映射
        gTeacherDict[teacher["id"]] = Teacher(teacher["id"], teacher["name"], teacher["department"], unsuitableParam)

    # 班级信息
    global classNum
    classCount = 1
    for cls in data.get("classes", []):
        classTypeTmp = -1
        if cls['type'] == "BUS":  # 商课班
            classTypeTmp = ClassType.BUS
        elif cls['type'] == "SCI":  # 理课班
            classTypeTmp = ClassType.SCI
        elif cls['type'] == "COMBO":  # 商理混合班
            classTypeTmp = ClassType.COMBO

        curClass = G12Class(classCount, classTypeTmp)

        # 在班级对象里面设置课程和老师信息
        curClass.setTeacherLst(cls['teachers'])
        curClass.setCourseLst(cls['courses'])

        classCount += 1
        gAllClassLst.append(curClass)

    classNum = len(gAllClassLst)  # 全局变量，记录班级数量

    # 课程信息
    global gCourseNum, gPEDay, gPEPeriod
    gCourseNum = 0
    for course in data.get("courses", []):
        gCourseNum += 1
        curCourseType = CourseType.COMMON
        if course['type'] == "BUS":
            curCourseType = CourseType.BUS
        elif course['type'] == "SCI":
            curCourseType = CourseType.SCI

        # 处理可选字段
        relative_id = course.get("relative_course_id", None)
        continuous_periods_num = course.get("continuous_periods_number", 1)
        oddEvenWeek = course.get("alternating_Odd_Even_Weeks", None)
        periods = course.get("required_periods", None)
        if course["name"] == COURSE_PHE:
            # 获取体育课的必修时段
            if periods is None:
                assert 0
            if len(periods) != 2:
                assert 0
            if periods[0][0] != periods[1][0]:
                assert 0
            if periods[0][1] + 1 != periods[1][1]:
                assert 0
            gPEDay = periods[0][0]
            gPEPeriod = periods[0][1]

        # 遍历班级数列，查看这门课在不在班级的课程列表中，如果在，创建课程对象并加入到allCourseLst
        for cls in gAllClassLst:
            if course['id'] in cls.getCourseLst():
                indx = cls.getCourseLst().index(course['id'])
                teacherID = cls.getTeacherLst()[indx]
                newCourse = Course(course['id'], course['name'], teacherID, curCourseType, course["amount"], cls)
                # 处理可选字段
                if relative_id is not None:
                    newCourse.setRelatedCourse(relative_id)
                if continuous_periods_num > 1:
                    newCourse.setContinuePeriodNum(continuous_periods_num)
                if periods is not None:
                    newCourse.setRequiredTime(periods)
                if oddEvenWeek is not None:
                    newCourse.setOddEvenWeek(oddEvenWeek)
                gAllCourseLst.append(newCourse)

    # 将对开课程存储的信息从ID转成对象
    for crs1 in gAllCourseLst:
        relatedID = crs1.getRelatedCourse()
        if relatedID is not None:
            for crs2 in gAllCourseLst:
                ID2 = crs2.getCourseID()
                if relatedID == ID2 and crs1.getTeachingClass().getID() == crs2.getTeachingClass().getID():
                    crs1.setRelatedCourse(crs2)
    # 将对单双周程存储的信息从ID转成对象
    for crs1 in gAllCourseLst:
        relatedID = crs1.getOddEvenWeek()
        if relatedID is not None:
            for crs2 in gAllCourseLst:
                ID2 = crs2.getCourseID()
                if relatedID == ID2 and crs1.getTeachingClass().getID() == crs2.getTeachingClass().getID():
                    crs1.setOddEvenWeek(crs2)

    return


"""
====================    主函数    ========================
"""
def runAutomaticSchedulingForWace(jsonStr, *args, **kwargs):

    # 解析json格式
    parseScheduleJson(jsonStr)

    global gCourseDNAPopulation

    # 创建种群
    generateCourseDNAPopulation()

    best_DNA, best_Fitness = None, float('inf')

    for gen in range(Generations):

        # 计算种群适应度
        fitness = computerFitness()

        # 0409 =======================start
        # 找到当前种群中最好的DNA
        for dnaIdx in range(PopulationSize):
            if fitness[dnaIdx] < best_Fitness:
                best_DNA = copy.deepcopy(gCourseDNAPopulation[dnaIdx])
                best_Fitness = fitness[dnaIdx]

        # print()
        # print("==========No.%d Best Fitness:%.4f" % (gen, best_Fitness))
        # print()

        if best_Fitness == 0: # 已经完全不冲突了，结束！！！
            break
        # 0409 ==========================end

        # 根据种群适应度排序
        # === 获取fitness排序后的索引
        sorted_indices = sorted(range(len(fitness)), key=lambda i: fitness[i])
        # === 根据排序的索引调整courseDNAPopulation的顺序
        DNAPop_Sorted = [gCourseDNAPopulation[i] for i in sorted_indices] # 最优的排在前面

        new_population = []
        for _ in range(PopulationSize // 2):
            parent1 = rouletteSort_selection(DNAPop_Sorted)
            parent2 = rouletteSort_selection(DNAPop_Sorted)

            if random.random() < crossover_rate:
                child1, child2 = pmx_crossover(parent1, parent2)
            else:
                child1, child2 = parent1[:], parent2[:]

            # 变异操作
            new_population.append(mutate(child1, mutation_rate))
            new_population.append(mutate(child2, mutation_rate))

        # 更新种群
        gCourseDNAPopulation = new_population

    for classIdx in range(classNum):
        printOneClassSchedule(best_DNA, classIdx)

    # 将课表转化为Json格式
    resultJson = genFinalCourseSchedule(best_DNA)

    return resultJson


# 生成输出的json格式
def genFinalCourseSchedule(CSDNA):

    # 基础信息
    data = {
        "class_count": classNum, # 班级数量
        "daily_Periods": dayPeriod, # 每天课程节数
        "time_table": {}
    }
    for i in range(classNum):
        clsWeekLst = [] # 某个班的课表初始化
        for j in range(schoolDays):
            crsDayLst = [] # 某天的课表初始化
            for k in range(dayPeriod):
                count = j * dayPeriod * classNum + k * classNum + i
                crsPeriodLst = [] # 同一个课时能上的课程（只有一门课程/对开课程/单双周课程）
                courseName = CSDNA[count][0].getName()
                if courseName == COURSE_PHE:
                    crsPeriodLst.append(CSDNA[count][0].getCourseID())
                    crsPeriodLst.append("PHE Teacher")
                else:
                    for m in range(len(CSDNA[count])):
                        crsPeriodLst.append(CSDNA[count][m].getCourseID())
                        crsPeriodLst.append(CSDNA[count][m].getTeacher())
                    if len(crsPeriodLst) > 2:
                        if CSDNA[count][0].getOddEvenWeek() is not None:
                            crsPeriodLst.append("OddEven")
                        elif CSDNA[count][0].getRelatedCourse() is not None:
                            crsPeriodLst.append("Related")
                        else:
                            assert 0
                crsDayLst.append(crsPeriodLst)
            clsWeekLst.append(crsDayLst)        # 添加该班级周几的课表
        data["time_table"][i + 1] = clsWeekLst  # 添加班级的课表

    return data






