<template>
  <div class="container">
    <!-- 顶部操作栏 -->
    <div class="header">
      <div class="filter-buttons">
        <el-button
          v-for="tag in allTags"
          :key="tag"
          :type="selectedTag === tag ? 'primary' : 'default'"
          @click="filterItems(tag)"
        >
          {{ tag }}
        </el-button>
      </div>
      <el-button type="primary" @click="openForm">新建项目</el-button>
    </div>

    <!-- 滚动项目列表 -->
    <div class="scroll-container">
      <el-table :data="filteredItems" style="width: 100%" @row-click="openDrawer">
        <el-table-column prop="name" label="项目名称" width="300" />
        <el-table-column prop="tags" label="标签">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags" :key="tag" class="tag">{{ tag }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 抽屉组件 (项目详情) -->
    <el-drawer v-model="drawerVisible" title="项目详情" direction="rtl">
      <p><strong>名称：</strong> {{ selectedItem?.name }}</p>
      <p><strong>排课类型：</strong> 
        <el-tag v-for="tag in selectedItem?.tags" :key="tag">{{ tag }}</el-tag>
      </p>

      <el-popconfirm title="确定要删除项目吗?"
        confirm-button-text="确认"
        cancel-button-text="取消"
        @confirm="deleteProject"
        >
        <template #reference>
          <el-button type="danger">删除项目</el-button>
        </template>
      </el-popconfirm>
      <el-button type="primary" @click="startEdit">编辑项目</el-button>

    </el-drawer>

    <!-- 新建项目对话框 -->
    <el-dialog v-model="dialogVisible" title="新建项目">
      <el-form :model="newItem" label-width="80px" ref="formRef" :rules="rules">
        <!-- 年份选择 -->
        <el-form-item label="课表年份" prop="year">
          <el-select v-model="newItem.year" placeholder="选择年份">
            <el-option v-for="year in yearOptions" :key="year" :label="year" :value="year" />
          </el-select>
        </el-form-item>

        <!-- 学期选择 -->
        <el-form-item label="课表学期" prop="semester">
          <el-select v-model="newItem.semester" placeholder="选择学期">
            <el-option v-for="semester in semesterOptions" :key="semester" :label="semester" :value="semester" />
          </el-select>
        </el-form-item>

        <!-- 年级选择 -->
        <el-form-item label="所属年级" prop="grade">
          <el-select v-model="newItem.grade" placeholder="选择年级">
            <el-option v-for="grade in gradeOptions" :key="grade" :label="grade" :value="grade" />
          </el-select>
        </el-form-item>

        <!-- 排课类型 -->
        <el-form-item label="排课类型" prop="tags">
          <el-radio-group v-model="newItem.tags">
            <el-radio v-for="tag in allTags" :key="tag" :value="tag">
              {{ tag }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="newItem.tags === '澳高'" label="每天课节" prop="dailyLessons">
          <el-radio-group v-model="newItem.dailyLessons">
            <el-radio :label="'7'">7节课</el-radio>
            <el-radio :label="'8'">8节课</el-radio>
          </el-radio-group>
        </el-form-item>

      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">提交</el-button>
      </template>
    </el-dialog>
  </div>

  <div class="pagination-container">
    <el-pagination
      :page-size="pageSize"
      :pager-count="11"
      layout="prev, pager, next"
      :total="totalItems"
      :current-page="currentPage"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '~/api' 
import { useWaceSetting } from '~/stores/waceSettings'
import { log } from "three/tsl";

const store = useWaceSetting()

const formRef = ref(); // 用来绑定 el-form 的引用
const router = useRouter()

const items = ref([]) // 替换原始 mock 数据
const totalItems = ref(0)  // 用于 pagination 的 total
const currentPage = ref(1) // 当前页码
const pageSize = ref(10)   // 每页条数（可以写死或动态）

// 新建项目的数据模型
const newItem = ref({
  name: '',
  tags: '',
  year: '',
  semester: '',
  grade: '',
  department: '',
  dailyLessons: '7'
});

// 可选项
const yearOptions = ref(["2025学年", "2026学年", "2027学年"]);
const semesterOptions = ref(['第一学期', '第二学期']);
const gradeOptions = ref(["10年级", "11年级", "12年级"]);


const fetchProjects = async (page = 1) => {
  try {
    const response = await api.get(`/api/project/list/?page=${page}`)
    items.value = response.data.results.map(item => ({
      id : item.id,
      name: item.name,
      tags: [mapProjectTypeToTag(item.project_type)],
      ...item,
    }))
    totalItems.value = response.data.count
    currentPage.value = page
  } catch (error) {
    console.error('获取项目失败', error)
  }
}

const handlePageChange = (newPage) => {
  fetchProjects(newPage)
}


// 项目类型映射为标签显示用
const mapProjectTypeToTag = (type) => {
  switch (type) {
    case 'project_ase':
      return '美高'
    case 'project_bse':
      return '英高'
    case 'project_wace':
      return '澳高'
    default:
      return '其他'
  }
}

// 页面加载时调用
onMounted(() => {
  fetchProjects()
})


const selectedTag = ref(""); // 选中的标签
const drawerVisible = ref(false); // 控制详情抽屉
const dialogVisible = ref(false); // 控制新建表单对话框
const selectedItem = ref(null); // 选中的项目

// 获取所有唯一标签
const allTags = computed(() => {
  return ["美高", "英高", "澳高", "其他"];
});

// 过滤项目
const filteredItems = computed(() => {
  return selectedTag.value
    ? items.value.filter((item) => item.tags.includes(selectedTag.value))
    : items.value;
});

// 切换筛选
const filterItems = (tag) => {
  selectedTag.value = selectedTag.value === tag ? "" : tag; // 再次点击取消筛选
};

// 打开表单
const openForm = () => {
  newItem.value = {
    name: '',
    tags: '',
    year: '',
    semester: '',
    grade: '',
    department: '',
    dailyLessons: '7',
  }
  dialogVisible.value = true;
};


// 校验规则
const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  tags: [{ required: true, message: '请选择排课类型', trigger: 'change' }],
  year: [{ required: true, message: '请选择年份', trigger: 'change' }],
  semester: [{ required: true, message: '请选择学期', trigger: 'change' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }]
};

// 提交表单
const submitForm = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      // 将新项目对象添加到项目列表
      items.value.push({ ...newItem.value });

      // 显示成功提示
      ElMessage.success("项目创建成功！");
      
      if(newItem.value.tags == "澳高")
        startCreateWACE()
      if(newItem.value.tags == "美高")
        startCreateASE()
    } else {
      // 显示失败提示
      ElMessage.error("请填写完整信息");
    }
  });
};


// 打开抽屉
const openDrawer = (row) => {
  selectedItem.value = row;
  drawerVisible.value = true;
};

const deleteProject = () => {
  const rawId = selectedItem.value.id;
  const id = rawId !== null ? Number(rawId) : -1;

  try {
    const response = api.post('/api/project/delete/', {
      id: id 
    });

    const data = response.data;
    window.location.reload()

  } catch (error) {
    console.error('删除项目失败:', error);
  }
};

const startCreateWACE = async () => {
  const name = `${newItem.value.year} ${newItem.value.semester} ${newItem.value.department} ${newItem.value.grade} 排课表`
  
  const payload = {
    type: 'project_wace',
    name: name,
  }

  try {
    const res = await api.post('/api/project/create/', {
      type: 'project_wace',
      name: name,
    })

    if (res.data.success) {
      const projectId = res.data.project_id
      console.log('✅ 创建成功，项目ID:', projectId)

      sessionStorage.setItem('wace_id', String(projectId))
      store.resetToDefaults()
      store.daySlots = newItem.value.dailyLessons
      router.push('/wace/step1')
    } else {
      console.error('❌ 创建失败:', res.data)
    }
  } catch (error) {
    console.error('❌ 请求错误:', error)
  }
}

const startCreateASE = async () => {
  const name = `${newItem.value.year} ${newItem.value.semester} ${newItem.value.tags} ${newItem.value.grade} 排课表`
  
  const payload = {
    type: 'project_ase',
    name: name,
  }

  try {
    const res = await api.post('/api/project/create/', {
      type: 'project_ase',
      name: name,
    })

    if (res.data.success) {
      const projectId = res.data.project_id
      console.log('✅ 创建成功，项目ID:', projectId)

      sessionStorage.setItem('ase_id', String(projectId))
      router.push('/ase/step1')
    } else {
      console.error('❌ 创建失败:', res.data)
    }
  } catch (error) {
    console.error('❌ 请求错误:', error)
  }
}

const startEdit = () => {
  if(selectedItem.value.tags.includes("澳高")){
    store.resetToDefaults()
    sessionStorage.setItem('wace_id', String(selectedItem.value.id))
    store.fetchDataFromBackend()
    router.push('/wace/result')
  }
  if(selectedItem.value.tags.includes("美高")){
    sessionStorage.setItem('ase_id', String(selectedItem.value.id))
    if (!aseCheck())
      router.push('/ase/result')
    else
      router.push('/ase/step1')

  }
}

const aseCheck = () => {
  const rawId = sessionStorage.getItem('ase_id');
  const id = rawId !== null ? Number(rawId) : -1;

  try {
    const response = api.get('/api/project/get', {
      params: { id }
    });

    const data = response.data;
    
    // 检查 courseData 是否存在并非空数组
    return  data && typeof data === 'object' && !Array.isArray(data) && Object.keys(data).length === 0
  } catch (error) {
    console.error('检查 courseData 失败:', error);
    return false;
  }
}

</script>

<style scoped>


.container {
  width: 80%;
  margin: auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.filter-buttons {
  display: flex;
  gap: 10px;
}

.scroll-container {
  max-height: 460px;
  overflow: auto;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.tag {
  margin-right: 5px;
}

.pagination-container {
  display: flex;
  justify-content: center; /* 居中 */
  margin-top: auto; /* 自动靠下 */
  padding: 10px 0; /* 增加一些间距 */
}
</style>
