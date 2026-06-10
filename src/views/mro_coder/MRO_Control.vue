<script setup>
import { ref } from 'vue';

const files = ref(null);

const handleFileChange = (event) => {
  files.value = event.target.files;
};

const uploadFiles = async () => {
  console.log( files);
  if (!files.value) return;
  const formData = new FormData();

  for (let i = 0; i < files.value.length; i++) {
    formData.append('files', files.value[i]);
  }

  try {
    const response = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      //method: 'GET',
      body: formData,
    });
    const result = await response.json();
    console.log(result);
  } catch (error) {
    console.error('Error uploading:', error);
  }
};
</script>

<template>
  <CRow>
    <CCol :xs="12">
      <CCard class="mb-4">
        <CCardHeader>
          <strong>MRO</strong> <small>upload form</small>
        </CCardHeader>
        <CCardBody>
          <div class="d-flex align-items-end gap-3">
            
            <div class="mb-0 flex-grow-1">
              <CFormLabel for="formFileMultiple">Multiple MRO files:</CFormLabel>
              <CFormInput id="formFileMultiple" type="file" multiple @change="handleFileChange" />
            </div>

            <div>
              <CButton color="primary" @click="uploadFiles">Upload Files</CButton>
            </div>
            
          </div>
        </CCardBody>

        <button @click="downloadCSV" class="btn btn-primary mb-3">
          Save as CSV
        </button>

        <table class="table table-sm">
          <thead>
            <tr>
              <th>#</th>
              <th>First Name</th>
              <th>Last Name</th>
              <th>Username</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">1</th>
              <td>Mark</td>
              <td>Otto</td>
              <td>@mdo</td>
            </tr>
            <tr>
              <th scope="row">2</th>
              <td>Jacob</td>
              <td>Thornton</td>
              <td>@fat</td>
            </tr>
            <tr>
              <th scope="row">3</th>
              <td colspan="2">Larry the Bird</td>
              <td>@twitter</td>
            </tr>
          </tbody>
        </table>

    
      </CCard>
    </CCol>
  </CRow>
</template>

<script setup>
import { ref } from 'vue';

// It is much easier to manage and export data if it lives in Vue state rather than parsing raw HTML
const tableData = ref([
  { id: 1, firstName: 'Mark', lastName: 'Otto', username: '@mdo', colspan: 1 },
  { id: 2, firstName: 'Jacob', lastName: 'Thornton', username: '@fat', colspan: 1 },
  // Replicating your Larry the Bird colspan example safely
  { id: 3, firstName: 'Larry the Bird', lastName: '', username: '@twitter', colspan: 2 }
]);

const downloadCSV = () => {
  // Define CSV Headers
  const headers = ['#', 'First Name', 'Last Name', 'Username'];
  
  // Map rows to CSV format
  const rows = tableData.value.map(row => [
    row.id,
    `"${row.firstName}"`, // Wrapping strings in quotes handles spaces nicely
    `"${row.lastName}"`,
    `"${row.username}"`
  ]);

  // Combine headers and rows, separating columns with commas and rows with newlines
  const csvContent = [headers, ...rows]
    .map(e => e.join(","))
    .join("\n");

  // Create a Blob from the CSV String
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  
  // Create a temporary hidden link element to trigger the download
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", "table_data.csv");
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
</script>