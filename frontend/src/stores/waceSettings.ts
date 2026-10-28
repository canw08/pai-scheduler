// src/stores/waceSetting.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '~/api'; // 使用你已有的封装过的 axios 实例
import { ElMessage } from 'element-plus'
import Login from '~/pages/nav/login.vue';

interface CourseItem {
  courseName: string
  courseId: number
  teacher: number
  teacherName: string
}

interface ClassItem {
  id: number
  name: string
  type: string // 新增：班级属性字段
  courses: CourseItem[]
}

export const useWaceSetting = defineStore('waceSetting', {
  state: () => ({
    currentId: -1,
    // 数据存储
    daySlots: 7,
    classData : ref<ClassItem[]>([
      { id: 1, name: '班级1 - 理科班', type: '理科班', courses: [] },
      { id: 2, name: '班级2 - 理科班', type: '理科班', courses: [] },
    ]),
    courseData: ref<{ id: number; course: string; quantity: number; continue: number ; associatedCourse?: number;associationType?:string }[]>([
        { id: 0, course: '', continue:1, quantity: 1},
        { id: 1, course: '', continue:1, quantity: 1}
      ]),
    teacherTimeSetting : ref<Record<number, boolean[][]>>({}),
    // courseTimeSetting : ref<Record<number, boolean[][]>>({}),
    peTimeSetting: [] as boolean[][],

    // 存储从后端获取的预设数据
    presets_teachers: ref<{ name: string; children: { id: number; name: string }[] }[]>([]),
    presets_courses: ref<{ course_name: string; course_type: string }[]>([]),
  }),

  actions: {
    async resetToDefaults() {
      this.currentId = -1;
      this.daySlots = 7;
      this.classData = <ClassItem[]>([
        { id: 1, name: '班级1 - 理科班', type: '理科班', courses: [] },
        { id: 2, name: '班级2 - 理科班', type: '理科班', courses: [] },
      ]);
      this.courseData = <{ id: number; course: string; quantity: number; continue: number; associatedCourse?: number; associationType?: string }[]>([
        { id: 0, course: '', continue: 1, quantity: 1 },
        { id: 1, course: '', continue: 1, quantity: 1 }
      ]);
      this.teacherTimeSetting = <Record<number, boolean[][]>>({});
      this.peTimeSetting = [] as boolean[][];
      this.presets_teachers = <{ name: string; children: { id: number; name: string }[] }[]>([]);
      this.presets_courses = <{ course_name: string; course_type: string }[]>([]);
    },

    // 发送数据到后端
    async sendDataToBackend() {
      // 获取 Pinia store 中的数据
      const data = {
        id: Number(sessionStorage.getItem('wace_id')),  // 获取 id
        config: {
          daySlots: this.daySlots,
          classData: this.classData,
          courseData: this.courseData,
          teacherTimeSetting: this.teacherTimeSetting,
          peTimeSetting: this.peTimeSetting,
        },
      };
      // 将数据转换为 JSON 格式
      const jsonData = JSON.stringify(data);

      try {
        // 使用 axios 发送 POST 请求
        const response = await api.post('/api/project/edit/', jsonData, {
          headers: {
            'Content-Type': 'application/json'
          }
        });

        // 处理响应结果
        console.log('数据已成功保存:', response.data);
        ElMessage.success('保存成功！');
      } catch (error) {
        console.error('保存数据时出错:', error);
        ElMessage.error('保存失败!');
      }
      console.log(this.courseData);
      
    },

    // 从后端获取数据
    async fetchDataFromBackend() {
      if(this.currentId != -1)
        return

      this.getPresets()
      
      const rawId = sessionStorage.getItem('wace_id');
      const id = rawId !== null ? Number(rawId) : -1;  // -1 作为默认值     

      try {
        const response = await api.get('/api/project/get', {
          params: { id }
        });
    
        const config = response.data.config;

        // 只在字段存在时才更新，保持默认值不被覆盖
        if (config.daySlots) this.daySlots = config.daySlots;
        if (config.classData) this.classData = config.classData;
        if (config.courseData) this.courseData = config.courseData;
        if (config.teacherTimeSetting) this.teacherTimeSetting = config.teacherTimeSetting;
        if (config.peTimeSetting) this.peTimeSetting = config.peTimeSetting;

        this.currentId = id
      } catch (error) {
        console.error('获取项目配置失败:', error);
      }
    },

    // 获取预设数据 (教师和课程)
    async getPresets() {
      try {
        const response = await api.get('/api/presets/export/', {
          params: { preset_type: "preset_wace" }
        });

        const presets = response.data.data;

        // 存储教师和课程数据到 store 中
        if (presets.teachers) {
          this.presets_teachers = presets.teachers;

          // 整理教师选项
          const grouped: Record<string, { id: number; name: string }[]> = {};
          presets.teachers.forEach((teacher: { teacher_id: number; teacher_name: string; department: string }) => {
            const dept = teacher.department;
            if (!grouped[dept]) grouped[dept] = [];
            grouped[dept].push({ id: teacher.teacher_id, name: teacher.teacher_name });
          });    

          this.presets_teachers = Object.entries(grouped).map(([dept, teachers]) => ({
            name: dept,
            children: teachers
          }));
        }

        if (presets.courses) {
          const filteredCourses = presets.courses
            .filter((course: { course_name: string }) => course.course_name)  // 过滤掉空课程
            .map((course: { course_name: string, course_type: string }) => ({
              course_name: course.course_name,
              course_type: course.course_type
            }));
          
          this.presets_courses = filteredCourses;
        }        
        
      } catch (error) {
        console.error('获取预设失败:', error);
      }
    }
    
  }

});
