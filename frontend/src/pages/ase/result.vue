<template>
  <div>
    <!-- 表格外层容器 -->
    <div
      style="overflow: auto; max-height: 600px; max-width: 100%; border: 1px solid #ddd; position: relative;"
    >
      <table ref="tableRef" class="custom-table">
        <thead>
          <tr>
            <th style="width: 100px;">Slot</th>
            <th
              v-for="(teacher, index) in teachers"
              :key="index"
              style="min-width: 180px;"
            >
              {{ teacher }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in formattedRows" :key="rowIndex">
            <td>{{ row.slot }}</td>
            <td
              v-for="(teacher, colIndex) in teachers"
              :key="colIndex"
              class="draggable-cell"
              :data-row="rowIndex"
              :data-col="colIndex"
            >
              {{ row[`teacher_${colIndex}`] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 左下角：重新排课按钮 -->
    <div style="position: fixed; bottom: 20px; left: 160px; z-index: 1000;">
      <el-popconfirm
        title="确定要重新排课吗？操作不可撤销"
        confirm-button-text="确认"
        cancel-button-text="取消"
        @confirm="regenerateSchedule"
      >
        <template #reference>
          <el-button type="warning">重新排课</el-button>
        </template>
      </el-popconfirm>
      <el-popconfirm
        title="确定要重置课表吗？操作不可撤销"
        confirm-button-text="确认"
        cancel-button-text="取消"
        @confirm="resetTable"
      >
        <template #reference>
          <el-button type="danger">重置课表</el-button>
        </template>
      </el-popconfirm>
    </div>

    <!-- 右下角：导出和发布按钮 -->
    <div
      style="position: fixed; bottom: 20px; right: 20px; display: flex; gap: 12px; z-index: 1000;"
    >
      <el-button type="primary" @click="exportToExcel">导出为 Excel</el-button>
      <el-button type="success" @click="">发布</el-button>
    </div>
  
  <div class="progress-container">
    <el-progress
      :percentage="percentage"
      :stroke-width="20"
      :text-inside="true"
      status="success"
      color="#409EFF"
      striped
    >
      <template #default="{ percentage }">
        <span class="custom-text">{{ percentage }}% 当前学生满足度</span>
      </template>
    </el-progress>
  </div>
</div>

</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import api from '~/api'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import interact from 'interactjs'
import { useRouter } from 'vue-router'

const router = useRouter()

const teachers = ref<string[]>([])
const formattedRows = ref<any[]>([])
const originalTable = ref<any[][]>([])
const tableRef = ref<HTMLElement | null>(null)

const percentage = ref(75)

const initDrag = async () => {
  await nextTick()
  const table = tableRef.value
  if (!table) return

  const cells = table.querySelectorAll<HTMLElement>('td.draggable-cell')

  let ghost: HTMLElement | null = null

  cells.forEach((cell) => {
    interact(cell).unset()

    interact(cell).draggable({
      inertia: true,
      listeners: {
        start(event: { target: HTMLElement }) {
          const el = event.target as HTMLElement
          ghost = el.cloneNode(true) as HTMLElement
          ghost.classList.add('ghost-cell')
          ghost.style.position = 'fixed'
          ghost.style.zIndex = '1000'
          ghost.style.opacity = '0.7'
          ghost.style.pointerEvents = 'none'
          document.body.appendChild(ghost)
        },
        move(event: { client: { x: number; y: number } }) {
          if (ghost) {
            ghost.style.left = `${event.client.x - 40}px`
            ghost.style.top = `${event.client.y - 30}px`
          }
        },
        end() {
          if (ghost) ghost.remove()
          ghost = null
          console.log(formattedRows.value);
          
        }
      }
    })

    interact(cell).dropzone({
      ondrop(event: { relatedTarget: HTMLElement; target: HTMLElement }) {
        const fromEl = event.relatedTarget as HTMLElement
        const toEl = event.target as HTMLElement

        const fromRow = Number(fromEl.dataset.row)
        const fromCol = Number(fromEl.dataset.col)
        const toRow = Number(toEl.dataset.row)
        const toCol = Number(toEl.dataset.col)

        const temp = formattedRows.value[fromRow][`teacher_${fromCol}`]
        formattedRows.value[fromRow][`teacher_${fromCol}`] = formattedRows.value[toRow][`teacher_${toCol}`]
        formattedRows.value[toRow][`teacher_${toCol}`] = temp
      }
    })
  })
}

onMounted(async () => {
  const res = await api.get(`/api/project/get?id=${Number(sessionStorage.getItem('ase_id')) || null}`)
  const table = res.data.table[1]

  if (!Array.isArray(table) || !Array.isArray(table[0])) {
    console.error('表格结构不合法:', table)
    return
  }

  teachers.value = table[0].map((t: string | null) => t ?? '')
  originalTable.value = JSON.parse(JSON.stringify(table))

  const courseRows = table.slice(1)
  formattedRows.value = courseRows.map((row, idx) => {
    const slot: Record<string, string> = { slot: `Slot ${idx + 1}` }
    row.forEach((val: any, tIdx: number) => {
      if (Array.isArray(val)) {
        // 处理数组（如 ["课程", "老师"]）
        slot[`teacher_${tIdx}`] = val.filter(Boolean).join(', ')
      } else {
        slot[`teacher_${tIdx}`] = val ?? ''
      }
    })

    return slot
  })
  initDrag()
})

const resetTable = () => {
  const table = originalTable.value
  const courseRows = table.slice(1)
  formattedRows.value = courseRows.map((row, idx) => {
    const slot: Record<string, string> = { slot: `Slot ${idx + 1}` }
    row.forEach((val: any, tIdx: number) => {
      if (Array.isArray(val)) {
        // 处理数组（如 ["课程", "老师"]）
        slot[`teacher_${tIdx}`] = val.filter(Boolean).join(', ')
      } else {
        slot[`teacher_${tIdx}`] = val ?? ''
      }
    })
    return slot
  })
  nextTick(initDrag)
}

const regenerateSchedule = () => { router.push('/ase/step1') }


const exportToExcel = () => {
  const exportData = formattedRows.value.map((row) => {
    const newRow: Record<string, string> = {
      Slot: row.slot
    }

    teachers.value.forEach((teacher, idx) => {
      newRow[teacher] = row[`teacher_${idx}`] ?? ''
    })

    return newRow
  })

  const worksheet = XLSX.utils.json_to_sheet(exportData)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, '课程表')

  const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([excelBuffer], { type: 'application/octet-stream' })
  saveAs(blob, '课程表.xlsx')
}
</script>

<style scoped>
.custom-table {
  width: 300%;
  border-collapse: collapse;
  table-layout: fixed;
    user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}
.custom-table th,
.custom-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
  cursor: grab;
}
.ghost-cell {
  background: #eee;
  border: 1px dashed #409EFF;
  padding: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}
.el-table {
  user-select: none;
}

.progress-container {
  /* display: flex;
  justify-content: center;
  align-items: center; */
  margin-top: 10px;
  margin-left: 10px;
  margin-right: 10px
}

</style>