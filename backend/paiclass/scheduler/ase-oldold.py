import random
import pprint
import numpy as np
from collections import defaultdict


class Course:
    def __init__(self, name, teacher, totalPeriods, id, bondWith=None, ):
        self.__name = name
        self.__teacher = teacher
        self.__totalPeriods = totalPeriods
        self.__bondWith = bondWith
        self.__id = id

    def getTotalPeriods(self):
        return self.__totalPeriods

    def getName(self):
        return self.__name

    def getTeacher(self):
        return self.__teacher

    def getBondWith(self):
        return self.__bondWith

    def getId(self):
        return self.__id


class Student:
    def __init__(self, name, favCourseNameList):
        self.__name = name
        self.__favCourseNameList = favCourseNameList

    def getName(self):
        return self.__name

    def getFavCourseNameList(self):
        return self.__favCourseNameList


def create_excludedCourseIndexDic(courseList: [Course]):
    excludedCourseIndexDic = dict({})
    for i in range(len(courseList)):
        excludedCourseIndexDic[courseList[i].getId()] = []
        for j in range(len(courseList)):
            if courseList[i].getTeacher() == courseList[j].getTeacher():
                excludedCourseIndexDic[courseList[i].getId()].append(j)

            elif courseList[i].getName() == courseList[j].getName():
                excludedCourseIndexDic[courseList[i].getId()].append(j)

    return excludedCourseIndexDic


def convertToName(totalSlot):
    nameList = [[] for i in range(len(totalSlot))]
    for i in range(len(totalSlot)):
        for j in range(len(totalSlot[i])):
            nameList[i].append(totalSlot[i][j].getName())
    for i in range(len(nameList)):
        print(nameList[i])


def outPutSchedule(totalSlot, corres, classroomList):
    courseTeacherNameList = [[[] for _ in range(len(classroomList))] for _ in range(len(totalSlot) + 1)]
    courseTeacherNameList[0] = classroomList
    for i in range(0, len(totalSlot)):
        for j in range(len(totalSlot[i])):
            courseTeacherNameList[i + 1][j] = [totalSlot[i][j].getName(), totalSlot[i][j].getTeacher()]
    return courseTeacherNameList


def backSchedule(courseTeacherNameList):
    schedule = [[None for _ in range(len(courseTeacherNameList[0]))] for _ in range(len(courseTeacherNameList) - 1)]

    for i in range(1, len(courseTeacherNameList)):
        for j in range(len(courseTeacherNameList[i])):
            if len(courseTeacherNameList[i][j]) != 0:
                schedule[i - 1][j] = Course(id=None, totalPeriods=1, name=courseTeacherNameList[i][j][0],
                                            teacher=courseTeacherNameList[i][j][1])

    # 移除 None 元素
    schedule = [[item for item in row if item is not None] for row in schedule]

    return schedule


def check_valid(schedule):
    for i in range(len(schedule)):
        for j in range(len(schedule[i])):
            for k in range(j + 1, len(schedule[i])):
                if schedule[i][j] is not None and schedule[i][k] is not None:
                    if schedule[i][j].getName() == schedule[i][k].getName():
                        return f"课程名冲突：请检查第{i}个slot的第{j}个课程({schedule[i][j].getName()})和第{k}个课程({schedule[i][k].getName()})"

                    if schedule[i][j].getTeacher() == schedule[i][k].getTeacher():
                        return f"老师冲突：请检查第{i}个slot的第{j}个课程({schedule[i][j].getName()})和第{k}个课程({schedule[i][k].getName()})"


def create_schedules(numOfClassrooms, numOfSlot, allCoursesList: [Course], excluededCourseIndexDic, bondDic):
    # 随机将课程放入slot里
    """
    :param numOfClassrooms:

    :param allCoursesList:
    :param numOfSlot:
    :return:
    1. 同slot不能有相同课程名
    2. 同slot不能有相同老师
    3. 同slot不能有
    allSlot[i][j] = 在第i个slot的第j个课
    创建一个互斥字典，表示选了这个课后在这个slot里面就不能选什么课了
    随机找一个slot，看能不能插进去
    对于所有数学课，只有四个slot能放slot，对于剩下的三个slot，有两个slot要和前面的四个slot对应（1对2）
    """
    noConflict = True
    while True:
        totalSlot = [[] for _ in range(numOfSlot)]
        countMath = 0
        mathSlotIndexList = []
        mathCourses = list(bondDic.keys())
        for i in range(len(allCoursesList)):
            # 这个if处理数学课
            if allCoursesList[i].getName() in mathCourses:
                # 如果有个教数学的老师教了其他课这里就有可能出问题死循环---------------------------------------------------------
                if countMath == 4:
                    # 会出现数学老师们彻底冲突到四个数学slot中一个都放不进去导致死循环
                    lst = mathSlotIndexList[:]
                    noConflict = True
                    while True:
                        if len(lst) == 0:
                            noConflict = False
                            break
                        num1 = random.randrange(len(lst))  # 随机下标 0 ≤ idx < len(lst)
                        num = lst.pop(num1)  # 弹出该元素

                        if len(totalSlot[num]) > numOfClassrooms:
                            continue

                        canIn = True
                        for course in totalSlot[num]:
                            if i in excluededCourseIndexDic[course.getId()]:
                                canIn = False
                                break
                        if canIn:
                            totalSlot[num].append(allCoursesList[i])
                            break
                    if not noConflict:
                        break
                else:
                    while True:
                        num = random.randint(0, numOfSlot - 1)
                        if len(totalSlot[num]) > numOfClassrooms:
                            continue

                        canIn = True
                        for course in totalSlot[num]:
                            if i in excluededCourseIndexDic[course.getId()]:
                                canIn = False
                                break
                        if canIn:
                            judge = True
                            for mathCourse in mathCourses:
                                if mathCourse in totalSlot[num]:
                                    judge = False
                                    break
                            if judge:
                                mathSlotIndexList.append(num)
                                countMath += 1
                            totalSlot[num].append(allCoursesList[i])
                            break
                continue
            while True:
                num = random.randint(0, numOfSlot - 1)
                if len(totalSlot[num]) > numOfClassrooms:
                    continue

                canIn = True
                for course in totalSlot[num]:
                    if i in excluededCourseIndexDic[course.getId()]:
                        canIn = False
                        break
                if canIn:
                    totalSlot[num].append(allCoursesList[i])
                    break

        if not noConflict:
            continue
        break

    # 分配数学课
    count = 0
    nonMathList = []
    for i in range(len(totalSlot)):
        if i not in mathSlotIndexList:
            nonMathList.append(i)

    corres = random.sample(nonMathList, 2)
    corresDic = dict({})
    randList = [0, 0, 1, 1]
    random.shuffle(randList)
    for i in range(len(mathSlotIndexList)):
        corresDic[mathSlotIndexList[i]] = corres[randList[i]]

    return totalSlot, corresDic


def create_population(numOfClassrooms, numOfSlot, allCoursesList: [Course], excluededCourseIndexDic, numOfPopulation,
                      bondDic):
    population = []
    populationCorres = []
    for i in range(numOfPopulation):
        schedule, corresDic = create_schedules(numOfClassrooms, numOfSlot, allCoursesList, excluededCourseIndexDic,
                                               bondDic)
        population.append(schedule)
        populationCorres.append(corresDic)

    return population, populationCorres


def produce(population, father, fatherCorres, mother, motherCorres, left, right, sameSlot, courseList,
            excludedCourseIndexDic,
            bondDic):
    # 可以将其改为纯粹从父辈中随机抽取几个slot去直接继承而不是连续的一段slot以确保随机
    # 但是我前面对数学slot和对应slot分布是随机的，所以不会影响到这里的随机性， 所以这里可以暂时不用管

    # todo
    # 数学课放不进去重新进行循环事需要将所有参数重新初始化
    # 数学solt和counselslot有重合
    countCannotReturn = 0
    for t in range(100000000):
        canReturn = True

        rand = random.randint(0, len(population[0]) - 1)
        left = rand
        right = rand + sameSlot
        mathCourses = list(bondDic.keys())

        findIndex = dict({})
        for i in range(len(courseList)):
            findIndex[courseList[i]] = i

        selected = {}
        for i in range(len(courseList)):
            selected[courseList[i]] = False
        child = [[] for _ in range(len(father))]

        # 环形数组思想， 对父亲的进行复制
        rebel = [[] for _ in range(len(father))]
        for i in range(left, right):
            i = i % len(father)
            for j in range(len(father[i])):
                child[i].append(father[i][j])
                rebel[i].extend(excludedCourseIndexDic[father[i][j].getId()])
                selected[father[i][j]] = True

        # 处理父亲数学课
        existedValue = set({})
        corresDic = dict({})
        mathSlot = []
        remainList = []
        for i in range(left, right):
            i = i % len(father)
            remainList.append(i)
        for i in range(left, right):
            i = i % len(father)
            if i in list(fatherCorres.keys()):
                mathSlot.append(i)
                if fatherCorres[i] in remainList:
                    if len(existedValue) < 2:
                        existedValue.add(fatherCorres[i])
                        corresDic[i] = fatherCorres[i]

        # 对母亲将能塞的塞进去

        for i in range(right, len(father) + left):
            i = i % len(father)
            for j in range(len(mother[i])):
                if selected[mother[i][j]]:
                    continue
                else:
                    # 这个if是对数学课特殊处理
                    if mother[i][j].getName() in mathCourses:
                        if i not in mathSlot:
                            if len(mathSlot) == 4:
                                continue
                            else:
                                if findIndex[mother[i][j]] not in rebel[i]:
                                    rebel[i].extend(excludedCourseIndexDic[mother[i][j].getId()])
                                    selected[mother[i][j]] = True
                                    child[i].append(mother[i][j])
                                    mathSlot.append(i)
                                    continue
                    # 数学课处理结束
                    if findIndex[mother[i][j]] not in rebel[i]:
                        rebel[i].extend(excludedCourseIndexDic[mother[i][j].getId()])
                        selected[mother[i][j]] = True
                        child[i].append(mother[i][j])

        # 数学
        # print(fatherCorres)
        remainList = []
        for i in range(right, len(father) + left):
            i = i % len(father)
            remainList.append(i)
        for i in range(right, len(father) + left):
            i = i % len(father)
            if len(mathSlot) == 4:
                break
            if i in motherCorres.keys():
                mathSlot.append(i)
                if motherCorres[i] in remainList:
                    if len(existedValue) < 2:
                        existedValue.add(motherCorres[i])
                        corresDic[i] = motherCorres[i]
        #         end

        # 预先去重，防止之前阶段重复
        mathSlot = list(dict.fromkeys(mathSlot))

        # 将母亲剩下的课程塞到 len 最小的 slot 里面
        childIndex = list(range(len(child)))
        for course, is_sel in selected.items():
            if not is_sel:
                # 按当前长度排序，得到真正的槽号列表
                childIndex.sort(key=lambda x: len(child[x]))
                name = course.getName()

                # —— 数学课特殊处理 ——
                if name in mathCourses:
                    placed = False

                    # (1) 如果还没放满 4 个数学槽，优先放到一个新槽
                    if len(mathSlot) < 4:
                        for slot in childIndex:
                            # 跳过已有数学槽或有冲突的槽

                            if slot in mathSlot or findIndex[course] in rebel[slot] or slot in existedValue:
                                continue
                            rebel[slot].extend(excludedCourseIndexDic[course.getId()])
                            child[slot].append(course)
                            mathSlot.append(slot)
                            selected[course] = True
                            placed = True
                            break
                        # 如果所有槽都试了仍未放进去
                        if not placed:
                            canReturn = False
                            # print("CountCannotReturn = " + str(
                            #     countCannotReturn) + f"数学课 {name} 无法放入任何已分配的数学槽")
                            break

                    # (2) 如果已经有 4 个数学槽，就只能放到这些已标记的数学槽里
                    else:
                        for slot in mathSlot:
                            if findIndex[course] in rebel[slot]:
                                continue
                            rebel[slot].extend(excludedCourseIndexDic[course.getId()])
                            child[slot].append(course)
                            selected[course] = True
                            placed = True
                            break
                        # 如果这些槽都放不下
                        if not placed:
                            canReturn = False
                            # print("CountCannotReturn = " + str(
                            #     countCannotReturn) + f"数学课 {name} 无法放入任何已分配的数学槽")
                            break

                    # 无论哪种情况，都跳过后续普通课程逻辑
                    continue

                # —— 普通课程 或 数学槽已满后的通用逻辑 ——
                for slot in childIndex:
                    if findIndex[course] in rebel[slot]:
                        continue
                    rebel[slot].extend(excludedCourseIndexDic[course.getId()])
                    child[slot].append(course)
                    selected[course] = True
                    break
                else:
                    # 普通课程也放不下就断言
                    assert 0, f"课程 {name} 无法放入任何槽"

        if canReturn is False:
            countCannotReturn += 1
            continue
        # 数学课特殊处理
        # 保证对应slot有两个
        count = 0
        nonMathList = []
        for i in range(len(child)):
            if i not in mathSlot:
                nonMathList.append(i)
        while len(existedValue) != 2:
            existedValue.add(random.sample(nonMathList, 1)[0])

        # existedDic用于帮助最后的对应关系， 保证每个被数学课对应slot可以尽量均分
        needAddMathSlot = mathSlot[:]
        existedDic = dict({})
        for toCorres in existedValue:
            existedDic[toCorres] = 0

        nowPutInMathCourses = list(corresDic.keys())
        for aMathSlot in nowPutInMathCourses:
            if corresDic[aMathSlot] in existedValue:
                existedDic[corresDic[aMathSlot]] += 1
            else:
                assert 0
            # 将needAddMathSlot剔除已经被选择过的
            if aMathSlot in needAddMathSlot:
                needAddMathSlot.remove(aMathSlot)
        for num in list(existedDic.keys()):
            while existedDic[num] < 2:
                # 防止mathslot少于4个
                if len(needAddMathSlot) == 0:
                    break
                slot = random.sample(needAddMathSlot, 1)[0]
                existedDic[num] += 1
                corresDic[slot] = num
                needAddMathSlot.remove(slot)

        # end
        if canReturn is True:
            return child, corresDic

        continue


def reproduction(population, populationCorres, courseList, excludedCourseIndexDic, sameSlot, bondDic):
    """
    :param population: population[i] = 课表, population[i][j]第j个slot
    :param sameSlot:继承父亲多少slot
    :return:
    创建一个selected代表选择的课
    从父亲那里继承 百分之rateOfSame的数据（直接把这个区间里的数据放到child的对应位置上），然后从母亲这里
    数学：如果父辈随机到的完全继承的slot有数学slot和其相对的对应slot，就将其的对应关系保留。 母辈填补剩下的空缺， 如果接下来还有缺失的对应关系， 将其随机分配
    """

    # 1. 用 zip 打包成 (元素1, 元素2) 的元组列表
    paired = list(zip(population, populationCorres))

    # 2. 原地打乱这个元组列表
    random.shuffle(paired)

    # 3. 如果需要再拆开成各自的列表
    population, populationCorres = zip(*paired)
    population = list(population)
    populationCorres = list(populationCorres)

    children = []
    childrenCorres = []
    numOfSlot = len(population[0])
    for i in range(0, len(population), 2):
        rand = random.randint(0, len(population[0]) - 1)
        child1, child1Corres = produce(population=population, father=population[i], fatherCorres=populationCorres[i],
                                       mother=population[i + 1],
                                       motherCorres=populationCorres[i + 1], left=rand, right=rand + sameSlot,
                                       sameSlot=sameSlot, courseList=courseList,
                                       excludedCourseIndexDic=excludedCourseIndexDic, bondDic=bondDic)
        child2, child2Corres = produce(population=population, father=population[i + 1],
                                       fatherCorres=populationCorres[i + 1],
                                       mother=population[i], motherCorres=populationCorres[i], left=rand,
                                       right=rand + sameSlot, sameSlot=sameSlot, courseList=courseList,
                                       excludedCourseIndexDic=excludedCourseIndexDic, bondDic=bondDic)
        children.append(child1)
        childrenCorres.append(child1Corres)
        children.append(child2)
        childrenCorres.append(child2Corres)

    newPopulation = children + population
    newPopulationCorres = childrenCorres + populationCorres

    return newPopulation, newPopulationCorres


# def preOpStudent(courseList: [Course], studentList: [Student]):
#     parallelDic = dict({})
#     for i in range(len(courseList)):
#         if courseList[i].getName() not in parallelDic.keys():
#             parallelDic[courseList[i].getName()] = 1
#         else:
#             parallelDic[courseList[i].getName()] += 1
#
#     numOfCourseNeedDic = dict({})
#     for i in range(len(studentList)):
#         for courseName in studentList[i].getFavCourseNameList():
#             if courseName not in numOfCourseNeedDic:
#                 numOfCourseNeedDic[courseName] = 1
#             else:
#                 numOfCourseNeedDic[courseName] += 1
#
#     avgCourseNameDic = dict({})
#     for i in range(len(courseList)):
#         avgCourseNameDic[courseList[i].getName()] = numOfCourseNeedDic[courseList[i].getName()] // parallelDic[
#             courseList[i].getName()]
#
#     return avgCourseNameDic


def fakeFitness(schedule, scheduleCorres, mathCourses, studentList, numOfselectiveCourseNeedBeSatisfied):
    """
    :param schedule:
    :param studentList:
    :return:
    维护一个distanceToAvgList， 使它可以表示距离平均值的距离。 然后对于每个学生选出来的5个课程。  对于schedule中的slot，
    我们优先选择平行班中被选择量最小的。 所以我们维护一个2D列表表示对于第i个课程，这个课程在哪些slot中出现。
    todo:
    最后我们维护一个最大教室承载量， 超过最大教室承载量我们就不让选这里的课
    corres 选了就选了另一个slot，特指数学

    """
    global lst

    # 优化 inDic 初始化
    inDic = defaultdict(list)
    for i, slot in enumerate(schedule):
        for course in slot:
            inDic[course.getName()].append(i)

    # 优化 numOfStudentInListDic 初始化
    numOfStudentInListDic = [defaultdict(int) for _ in range(len(schedule))]

    for i, slot in enumerate(schedule):
        for course in slot:
            numOfStudentInListDic[i][course.getName()] = 0
    numOfSatisfiedStudents = 0
    canStudentSatisfyDic = {}
    for student in studentList:
        favCourseNameList = student.getFavCourseNameList()
        favCourse2DIndexList = [[] for i in range(len(favCourseNameList))]
        for i in range(len(favCourseNameList)):
            favCourse2DIndexList[i].extend(inDic[favCourseNameList[i]])
        # 对于每个课程，将其存在的slot按从人数低往高排序
        for i in range(len(favCourse2DIndexList)):
            favCourse2DIndexList[i].sort(key=lambda x: numOfStudentInListDic[x][favCourseNameList[i]])
        mustChosenAnsIndex = []
        selectiveAnsIndex = []
        allAnsIndex = []
        selectedCoureses = []
        corresIndex = []

        def dfs(currentCourseIndex):
            if len(mustChosenAnsIndex) == 3 and (len(favCourseNameList) - 3 == len(selectiveAnsIndex) or len(
                    selectiveAnsIndex) == numOfselectiveCourseNeedBeSatisfied):
                return True
            if currentCourseIndex >= len(favCourse2DIndexList):
                return False
            for slotIndex in favCourse2DIndexList[currentCourseIndex]:
                # if 为True就是数学，Flase进非数学
                if favCourseNameList[currentCourseIndex] in mathCourses:
                    if slotIndex not in allAnsIndex:
                        if scheduleCorres[slotIndex] not in allAnsIndex:
                            selectedCoureses.append(favCourseNameList[currentCourseIndex])
                            allAnsIndex.append(slotIndex)
                            mustChosenAnsIndex.append(slotIndex)
                            corresIndex.append(scheduleCorres[slotIndex])
                            if dfs(currentCourseIndex + 1) is True:
                                return True
                            else:
                                del selectedCoureses[-1]
                                del allAnsIndex[-1]
                                del mustChosenAnsIndex[-1]
                                del corresIndex[-1]

                else:
                    if slotIndex not in allAnsIndex:
                        if slotIndex not in corresIndex:
                            # 必修课
                            if currentCourseIndex < 3:
                                selectedCoureses.append(favCourseNameList[currentCourseIndex])
                                allAnsIndex.append(slotIndex)
                                mustChosenAnsIndex.append(slotIndex)
                                if dfs(currentCourseIndex + 1) is True:
                                    return True
                                else:
                                    del selectedCoureses[-1]
                                    del allAnsIndex[-1]
                                    del mustChosenAnsIndex[-1]
                            # 选修课
                            else:
                                selectedCoureses.append(favCourseNameList[currentCourseIndex])
                                allAnsIndex.append(slotIndex)
                                selectiveAnsIndex.append(slotIndex)
                                if dfs(currentCourseIndex + 1) is True:
                                    return True
                                else:
                                    del selectedCoureses[-1]
                                    del allAnsIndex[-1]
                                    del selectiveAnsIndex[-1]
            # 如果是selective的课，那就可以将其不选
            if currentCourseIndex >= 3:
                if dfs(currentCourseIndex + 1) is True:
                    return True
            return False

        if dfs(currentCourseIndex=0) is True:
            #     判断可不可以选出来， 如可以更新numOfStudentInListDic

            numOfSatisfiedStudents += 1
            canStudentSatisfyDic[student.getName()] = [True, allAnsIndex[:] + corresIndex, selectedCoureses]
            for i in range(len(allAnsIndex)):
                numOfStudentInListDic[allAnsIndex[i]][favCourseNameList[i]] += 1
        else:
            canStudentSatisfyDic[student.getName()] = [False, None, None]
    return numOfSatisfiedStudents / len(studentList), canStudentSatisfyDic


def selection(bondDic, population, populationCorres, studentList, weight, numOfselectiveCourseNeedBeSatisfied,
              trueArithmetic_falseGeometric):
    """
    :param population:
    :param weight: 第i个的抽中概率是第i-1个抽中概率的weight倍
    :return:
    用适应度做出就近轮盘赌
    就近轮盘赌：
        一次性抽一百个随机数，然后通过排名轮盘赌去抽人，注意：如果这一百个随机数中有随机数在已经被选过的区间，那就近选择（靠近下面区间就选下面区间的数，靠近上面区间就选上面的数）

    to do 将这里在筛选过后将剩下的population依旧能和corres一一下标对应
    """

    notSelected = [True for i in range(len(population))]
    sortWeight = [1]
    for i in range(1, len(population)):
        if trueArithmetic_falseGeometric is True:
            sortWeight.append(sortWeight[i - 1] + weight)
        else:
            sortWeight.append(sortWeight[i - 1] * weight)

    fitnessList = []
    maxFitness = 0
    bestCorres = populationCorres[0]
    bestSchedule = population[0]
    bestCanStudentSatisfyDic = {}
    for i in range(len(population)):
        fitness, canStudentSatisfyDic = fakeFitness(population[i], populationCorres[i], list(bondDic.keys()),
                                                    studentList,
                                                    numOfselectiveCourseNeedBeSatisfied)
        fitnessList.append(fitness)
        if maxFitness < fitnessList[i]:
            bestCanStudentSatisfyDic = canStudentSatisfyDic
            maxFitness = fitnessList[i]
            bestSchedule = population[i]
            bestCorres = populationCorres[i]

    # 把两个列表配成一对
    paired = list(zip(fitnessList, population, populationCorres))

    # 按 fitnessList 排序
    paired.sort(key=lambda x: x[0])

    # 提取排序后的 population
    sorted_population = [x[1] for x in paired]
    populationIndex = []
    for i in range(len(sorted_population)):
        populationIndex.append(i)
    s = sum(sortWeight)
    for i in range(len(sortWeight)):
        sortWeight[i] = sortWeight[i] / s
    # 从种群中根据权重选择 len//2 个不重复的个体
    selected_populationIndex = np.random.choice(populationIndex, size=len(sorted_population) // 2, replace=False,
                                                p=sortWeight)

    selected_population = []
    selected_population_corres = []
    sorted_population_corres = [x[2] for x in paired]
    for i in range(len(selected_populationIndex)):
        selected_population.append(sorted_population[selected_populationIndex[i]])
        selected_population_corres.append(sorted_population_corres[selected_populationIndex[i]])

    if len(selected_population) != len(population) // 2:
        assert 0

    return maxFitness, bestSchedule, bestCorres, selected_population, selected_population_corres, bestCanStudentSatisfyDic


def align_schedule_by_teacher(finalSchedule):
    """
    把 finalSchedule（7 个 slot 的二维列表）重排为“行=slot、列=老师”格式，
    相同老师的课在同一列，空位用 None 填充。
    返回 (grid, teachers)，其中：
      - grid 是一个 len(finalSchedule) x len(teachers) 的列表，
        grid[i][j] 要么是 Course，要么是 None。
      - teachers 是对应的列名列表，按首次出现顺序。
    """
    # 1) 收集所有老师（按首次出现顺序）
    teachers = []
    for slot in finalSchedule:
        for course in slot:
            t = course.getTeacher()
            if t not in teachers:
                teachers.append(t)

    # 2) 建立老师→列索引映射
    teacher_to_col = {t: idx for idx, t in enumerate(teachers)}

    # 3) 初始化空表格
    rows = len(finalSchedule)
    cols = len(teachers)
    grid = [[None for _ in range(cols)] for _ in range(rows)]

    # 4) 填入课程
    for row_idx, slot in enumerate(finalSchedule):
        for course in slot:
            col_idx = teacher_to_col[course.getTeacher()]
            grid[row_idx][col_idx] = course

    return grid, teachers


import random


def reorder_list(lst, first_idx_list, second_idx_list):
    # 参数校验
    if len(lst) != 7:
        raise ValueError("原始列表长度必须为7")
    if not (0 <= len(first_idx_list) <= 4):
        raise ValueError("first_idx_list 长度需小于等于4")
    if len(second_idx_list) != 2:
        raise ValueError("second_idx_list 长度必须为2")
    # 提取三个部分
    first_elems = [lst[i] for i in first_idx_list]
    second_elems = [lst[i] for i in second_idx_list]
    used = set(first_idx_list) | set(second_idx_list)
    remaining = [lst[i] for i in range(7) if i not in used]

    # 构造结果
    res = [None] * 7
    rem_iter = iter(remaining)

    # 填前四位
    for pos in range(4):
        if pos < len(first_elems):
            res[pos] = first_elems[pos]
        else:
            res[pos] = next(rem_iter)
    # 填第五、第六位（下标4,5）
    res[4], res[5] = second_elems
    # 最后一位
    res[6] = next(rem_iter)

    return res


def formatSchedule(schedule, corres):
    schedule = schedule[:]

    def invert_dict(d):
        inverted = {}
        for key, value in d.items():
            # 如果 value 还没在 inverted 中，就创建一个空列表
            inverted.setdefault(value, []).append(key)

        return inverted

    peDic = invert_dict(corres)
    peList = list(sorted(peDic.keys()))
    if len(peDic[peList[0]]) < len(peDic[peList[1]]):
        peList[0], peList[1] = peList[1], peList[0]
    mathSlotIndexList = []
    for i in range(len(peList)):
        mathSlotIndexList.extend(peDic[peList[i]])
    schedule = reorder_list(schedule, mathSlotIndexList, peList)
    PElist = [Course(name="PE" + str([0, 1]), id=None, totalPeriods=None, teacher="PETeachers"),
              Course(name="PE" + str([2, 3]), id=None, totalPeriods=None, teacher="PETeachers")]
    schedule[4].append(PElist[0])
    schedule[5].append(PElist[1])
    return schedule


def runAutomaticSchedulingForAse(config,task, weight=1.045, sameSlot=1):
    classRoom = [
        "California",
        "Nevada",
        "Ohio",
        "Minnesota",
        "Utah",
        "Florida",
        "Kansas",
        "Arizona",
        "Texas",
        "Georgia",
        "Colorado",
        "Oregon",
        "Louisiana",
        "Michigan",
        "Maryland",
        "Pennsylvania",
        "Hawaii",
        "Rhode Island",
        "Sports"
    ]
    capacityOfClassroom = 20
    numOfClassrooms = len(classRoom)
    numOfSlot = 7
    numOfPopulation = 200
    trueArithmetic_falseGeometric = False
    numOfselectiveCourseNeedBeSatisfied = 3

    # courseNameList = [
    #     "English 200: Intermediate ELA", "English 300: English Writing and Analysis", "TOEFL 1",
    #     "TOEFL 2", "English 500: English College Writing", "AP Computer Science Principles",
    #     "AP Physics C: Mechanics", "Algebra I", "Algebra II", "Pre-Calculus", "AP Pre-Calculus", "AP Microeconomics",
    #     "World History",
    #     "Performance Art",
    #
    #     "English 200: Intermediate ELA", "English 400: English Literature and Rhetoric", "English Foundation 1",
    #     "TOEFL 1", "English Foundation 2", "SAT 1", "AP Computer Science A", "Biology",
    #     "Algebra I", "Algebra II", "AP Statistics",
    #     "AP Microeconomics", "World Geography", "Chinese Literature",
    #
    #     "English 100: Introduction to ELA", "English 300: English Writing and Analysis", "Pre-AP English 2",
    #     "English Foundation 1", "Intermediate English 1 (IELTS)", "TOEFL 2",
    #     "English 500: English College Writing", "Psychology", "Chemistry",
    #     "Calculus", "Statistics", "Pre-Calculus", "AP Calculus", "Business and Economics", "AP Human Geography",
    #
    #     "English 200: Intermediate ELA", "English 300: English Writing and Analysis",
    #     "English 400: English Literature and Rhetoric", "Digtal Media Techonology", "English Foundation 2", "SAT 2",
    #     "AP Psychology", "Physics",
    #     "Chemistry", "Statistics", "Pre-Calculus", "AP Calculus", "AP Chemistry", "Studio Art",
    #
    #     "English Foundation 1", "TOEFL 2", "AP Psychology",
    #     "AP Physics C: Electricity and Magnetism", "AP Biology",
    #     "Economics Honor", "AP World History", "Advanced Studio Art",
    #
    #     "English 400: English Literature and Rhetoric", "English Foundation 2 (IELTS)",
    #     "TOEFL 1", "English Foundation 2", "AP English Language and Composition",
    #     "AP Computer Science Principles", "Physics", "Business and Economics", "Advanced Studio Art",
    #
    #     "Pre-AP English 1", "Computer Science A Honor", "TOEFL 2",
    #     "TOEFL 1", "English Foundation 2", "English Literature and Composition", "Psychology",
    #     "Chemistry", "Biology", "Japanese",
    #     "World Geography", "AP Macroeconomics", "World History", "Advanced Performance Art", "Studio Art"
    # ]
    #
    # bondDic = {
    #     "Pre-Calculus": 1, "AP Pre-Calculus": 1, "Algebra I": 1, "Algebra II": 1, "Statistics": 1, "AP Statistics": 1,
    #     "Calculus": 1, "AP Calculus": 1,
    # }
    #
    # teacherList = [
    #     "Natasha", "Bridgette", "赵赛茜/刘永芳", "宋琦/付梦洁", "Thomas", "李程", "刘小彤", "吴栩桐", "胡子瑜", "孙懿",
    #     "那玲玲", "顾贤", "谷鑫鑫", "王子赫",
    #
    #     "Natasha", "Irene", "刘永芳/赵赛茜", "赵赛茜/刘永芳", "付梦洁/宋琦", "杨宏有", "胡哲", "方圆", "吴栩桐",
    #     "胡子瑜", "麦合", "顾贤", "刘奕彤",
    #     "王子赫",
    #
    #     "Natasha", "Bridgette", "Irene", "刘永芳/赵赛茜", "杨宏有", "宋琦/付梦洁", "Thomas", "卢露雯", "文东琪",
    #     "胡子瑜", "麦合", "那玲玲", "孙懿", "任媛",
    #     "刘奕彤",
    #
    #     "Natasha", "Bridgette", "Irene", "吴栩桐", "付梦洁/宋琦", "杨宏有", "卢露雯", "刘小彤", "文东琪", "麦合",
    #     "那玲玲", "孙懿",
    #     "王曼曼", "李琳",
    #
    #     "刘永芳/赵赛茜", "宋琦/付梦洁", "卢露雯", "刘小彤", "方圆", "任媛", "谷鑫鑫", "李琳",
    #
    #     "Irene", "刘永芳/赵赛茜", "赵赛茜/刘永芳", "付梦洁/宋琦", "Thomas", "李程", "刘小彤", "任媛", "李琳",
    #
    #     "Bridgette", "吴栩桐", "宋琦/付梦洁", "赵赛茜/刘永芳", "付梦洁/宋琦", "杨宏有", "卢露雯", "文东琪", "方圆",
    #     "刘睿佳", "刘奕彤",
    #     "顾贤", "谷鑫鑫", "王子赫", "李琳"
    # ]
    #
    #
    #
    # totalPeriodsList = [1] * 89
    #
    # import pickle
    #
    # # 从文件读取数据
    # import pandas as pd
    #
    # # 文件路径
    # file_path = "ase导入文件.xlsx"
    #
    # # 读取第三个工作表（根据名称 "学生信息"）
    # df = pd.read_excel(file_path, sheet_name="学生信息")
    #
    # # 将 DataFrame 转换为二维列表
    # data_list = df.values.tolist()
    #
    # # 打印二维列表
    # # for row in data_list:
    #     # print(row)
    #
    # studentNames = []
    # for i in range(len(data_list)):
    #     studentNames.append(data_list[i][0])
    #     del data_list[i][0]
    # favorite5Courses = data_list

    courseNameList, bondDic, teacherList, favorite5Courses, studentNames = parse_config(config)
    totalPeriodsList = [1] * 89

    for i in range(len(favorite5Courses)):
        j = 0
        while j < len(favorite5Courses[i]):
            if favorite5Courses[i][j] not in courseNameList:
                # print(favorite5Courses[i][j])
                del favorite5Courses[i][j]
                j -= 1
            j += 1
    count = 0
    for i in range(len(favorite5Courses)):
        while len(favorite5Courses[i]) > 10:
            del favorite5Courses[i][-1]

        # print("number of courses is " + str(len(favorite5Courses[i])))
        # print("favorite5Course " + str(i) + ": ", favorite5Courses[i])
        if len(favorite5Courses[i]) < 6:
            count += 1
            print(count)
    print("-------", count)

    mathCourses = list(bondDic.keys())

    studentNames = studentNames

    studentList = [Student(studentNames[i], favorite5Courses[i]) for i in range(len(studentNames))]
    for i in range(len(studentList)):
        print(studentList[i].getName(), studentList[i].getFavCourseNameList())

    # 1. 打包成 对的列表 调试：
    pairs = list(zip(courseNameList, teacherList))

    # 2. 随机打乱
    random.shuffle(pairs)

    # 3. 解包回两个列表
    courseNameList, teacherList = zip(*pairs)

    # 4. （可选）如果你需要它们仍然是列表而非元组
    courseNameList = list(courseNameList)
    teacherList = list(teacherList)

    courseList = [Course(courseNameList[i], teacherList[i], totalPeriodsList[i], i) for i in
                  range(len(courseNameList))]

    excludedCourseIndexDic = create_excludedCourseIndexDic(courseList)
    population, populationCorres = create_population(numOfClassrooms=numOfClassrooms, numOfSlot=numOfSlot,
                                                     allCoursesList=courseList,
                                                     excluededCourseIndexDic=excludedCourseIndexDic,
                                                     numOfPopulation=numOfPopulation, bondDic=bondDic)
    for i in range(1000):
        newPopulation, newPopulationCorres = reproduction(population=population, populationCorres=populationCorres,
                                                          courseList=courseList,
                                                          excludedCourseIndexDic=excludedCourseIndexDic,
                                                          sameSlot=sameSlot, bondDic=bondDic)

        maxFit, bestSche, bestCorres, population, populationCorres, bestCanStudentSatisfyDic = selection(
            bondDic=bondDic, population=newPopulation,
            populationCorres=newPopulationCorres,
            studentList=studentList, weight=weight,
            numOfselectiveCourseNeedBeSatisfied=numOfselectiveCourseNeedBeSatisfied,
            trueArithmetic_falseGeometric=trueArithmetic_falseGeometric)
        # print(maxFit)
        task.progress = int(maxFit * 100)
        task.save()
        if i > 250:
            bestSche = formatSchedule(schedule=bestSche, corres=bestCorres)
            grid, teachers = align_schedule_by_teacher(bestSche)
            # 打印表头
            print("Slot\\Teacher", teachers)
            display = [teachers[:]]
            for index, row in enumerate(grid):
                # row 是一个长度为 len(teachers) 的列表
                display.append([course.getName() if course else None for course in row])
            print(display)
            convertToName(bestSche)
            # convertToName(bestSche)
            output = outPutSchedule(bestSche, bestCorres, classRoom)
            print("课程和老师名字课表：   ")
            for i in range(len(output)):
                print(output[i])
            print("number of math slot is " + str(len(bestCorres)))

            # exit(0)
            return [maxFit, output]
        # print("------------------------" + str(i) + "------------------------")


def append_to_file(file_path, data):
    """
    将数据追加到 txt 文件并换行
    :param file_path: 文件路径
    :param data: 要写入的数据（可以是字符串、列表或数字）
    """
    # 将数据转换为字符串并在末尾加上换行符
    data_str = str(data) + "\n"

    # 以追加模式打开文件，并将数据写入
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(data_str)


def afterDrag(config, courseTeacherList, numOfselectiveCourseNeedBeSatisfied = 3):
    courseNameList, bondDic, teacherList, favorite5Courses, studentNames = parse_config(config)
    studentList = [Student(studentNames[i], favorite5Courses[i]) for i in range(len(studentNames))]

    for i in range(len(favorite5Courses)):
        j = 0
        while j < len(favorite5Courses[i]):
            if favorite5Courses[i][j] not in courseNameList:
                # print(favorite5Courses[i][j])
                del favorite5Courses[i][j]
                j -= 1
            j += 1
    count = 0
    for i in range(len(favorite5Courses)):
        while len(favorite5Courses[i]) > 10:
            del favorite5Courses[i][-1]

        # print("number of courses is " + str(len(favorite5Courses[i])))
        # print("favorite5Course " + str(i) + ": ", favorite5Courses[i])
        if len(favorite5Courses[i]) < 6:
            count += 1


    #print(courseTeacherList)
    schedule = backSchedule(courseTeacherList)

    convertToName(schedule)
    fitness = 0
    check = check_valid(schedule)
    if check is not None:
        return [False, check]
    else:
        corres = {0: None, 1: None, 2: None, 3: None, }
        for i in range(len(courseTeacherList)):
            for j in range(len(courseTeacherList[i])):
                # print(courseTeacherList[i][j])
                if len(courseTeacherList[i][j]) > 1 and courseTeacherList[i][j][1] == "PETeachers":
                    #                     PE[1, 2]`
                    corres[int(courseTeacherList[i][j][0][3:4])] = i
                    corres[int(courseTeacherList[i][j][0][6:7])] = i
        fitness = fakeFitness(schedule=schedule, scheduleCorres=corres, mathCourses=list(bondDic.keys()),
                              studentList=studentList,
                              numOfselectiveCourseNeedBeSatisfied=numOfselectiveCourseNeedBeSatisfied)[0]
        print(fitness)
        return [True, str(fitness * 100)]


from typing import List, Dict, Any, Tuple


def parse_config(data: Dict[str, Any]) -> Tuple[List[str], Dict[str, int], List[str], List[List[str]], List[str]]:
    config = data

    courseNameList: List[str] = []
    teacherList: List[str] = []
    bondDic: Dict[str, int] = {}
    favorite5Courses: List[List[str]] = []
    studentNames: List[str] = []

    # 处理非数学课
    for item in config.get("非数学课设置", []):
        course = item["课程名称"]
        teacher = item["老师名称"]
        count = item["班级数"]
        for _ in range(count):
            courseNameList.append(course)
            teacherList.append(teacher)

    # 处理数学课
    for item in config.get("数学课设置", []):
        course = item["课程名称"]
        teacher = item["老师名称"]
        count = item["班级数"]
        bondDic[course] = count
        for _ in range(count):
            courseNameList.append(course)
            teacherList.append(teacher)

    # 处理学生信息
    for student in config.get("学生信息", []):
        studentNames.append(student.get("学生姓名", ""))
        favs = []
        for key, value in student.items():
            if key != "学生姓名":
                favs.append(value)
        favorite5Courses.append(favs)

    return courseNameList, bondDic, teacherList, favorite5Courses, studentNames


# # 示例用法
# file_path = "output.txt"
# if __name__ == '__main__':
#     while True:
#         main(9, 1)
#         # append_to_file(file_path, main(round(random.uniform(1.0001, 1.1), 5), random.randint(1, 6)))
#


"""
1/55 2/55 3/55 4/55 5/55....10/55
1
初始化筛选-------------
进化结束时间点
轮盘赌排名改进
适应度时间优化--不太
"""
