import json

def transform_schedule(input_data, extra_data):
    output = {
        "classes": [],
        "courses": [],
        "teachers": []
    }

    teacher_ids = set()
    classData = input_data["classData"]
    courseData = input_data["courseData"]
    teacherTimeSetting = input_data.get("teacherTimeSetting", {})
    peTimeSetting = input_data.get("peTimeSetting", [])

    # 建立老师id到姓名、部门的映射
    teacher_info_map = {str(t["teacher_id"]): (t["teacher_name"], t["department"]) for t in extra_data["teachers"]}
    # 建立课程名到课程类型的映射
    course_type_map = {c["course_name"]: c["course_type"] for c in extra_data["courses"]}

    # 确定 PE 课程的ID：当前最大ID + 1
    max_course_id = max(c["id"] for c in courseData)
    pe_course_id = max_course_id + 1

    # 处理 classes
    for cls in classData:
        classType = "COMBO"
        if cls["type"] == "理科班":
            classType = "SCI"
        elif cls["type"] == "商科班":
            classType = "BUS"

        class_entry = {
            "name": cls["name"],
            "type": classType,
            "teachers": [],
            "courses": []
        }
        for course in cls["courses"]:
            teachers = course.get("teacher")
            if teachers and teachers is not None:
                teacher_id = str(teachers).zfill(3)
                class_entry["teachers"].append(teacher_id)
                teacher_ids.add(teacher_id)
            else:
                class_entry["teachers"].append("")
            # 找到对应的课程id
            for c in courseData:
                if c["course"] == course["courseName"]:
                    class_entry["courses"].append(c["id"])
                    break

        # 每个班级加一门 PHE 课
        class_entry["teachers"].append("")  # PE没有固定老师
        class_entry["courses"].append(pe_course_id)  # 用新的连续id

        output["classes"].append(class_entry)

    # 处理 courses
    for c in courseData:
        course_entry = {
            "id": c["id"],
            "name": c["course"],
            "type": course_type_map.get(c["course"], "COMMON"),  # 根据额外数据匹配
            "amount": c["quantity"]
        }
        if "associatedCourse" in c and c["associatedCourse"] is not None:
            if c.get("associationType") == "单双周课程":
                course_entry["alternating_Odd_Even_Weeks"] = c["associatedCourse"]
            else:
                course_entry["relative_course_id"] = c["associatedCourse"]

        output["courses"].append(course_entry)

    # 添加 PHE 课程到 courses
    pe_required_period = []
    for slot_index, day_slots in enumerate(peTimeSetting):
        for day_index, available in enumerate(day_slots):
            if available:
                pe_required_period.append([day_index, slot_index])

    pe_course_entry = {
        "id": pe_course_id,
        "name": "PHE",
        "type": "COMMON",
        "amount": len(pe_required_period)
    }

    if pe_required_period:
        pe_course_entry["required_periods"] = pe_required_period

    output["courses"].append(pe_course_entry)

    # 处理 teachers
    for tid in sorted(teacher_ids):
        raw_tid = str(int(tid))  # 001 -> 1
        teacher_name, department = teacher_info_map.get(raw_tid, ("", "WACE"))

        teacher_entry = {
            "id": tid,
            "name": teacher_name,
            "department": department
        }
        # 提取 teacherTimeSetting
        if raw_tid in teacherTimeSetting:
            unsuitable = []
            time_matrix = teacherTimeSetting[raw_tid]
            for slot_index, day_slots in enumerate(time_matrix):
                for day_index, available in enumerate(day_slots):
                    if available is True:
                        unsuitable.append([day_index, slot_index])
            if unsuitable:
                teacher_entry["unsuitable_period"] = unsuitable

        output["teachers"].append(teacher_entry)

    return output
