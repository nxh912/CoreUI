<script setup>
import { ref } from 'vue';

const files = ref(null);
const isLoading = ref(false);       // tracks whether upload is in progress
const reportResult = ref(null);     // stores the API response

const handleFileChange = (event) => {
  files.value = event.target.files;
};

const uploadFiles = async () => {
  if (!files.value) return;

  const formData = new FormData();
  for (let i = 0; i < files.value.length; i++) {
    formData.append('files', files.value[i]);
  }

  isLoading.value = true;       // show placeholders while waiting
  reportResult.value = null;    // clear any previous result

  try {
    const response = await fetch('http://127.0.0.1:8000/upload', {
      method: 'POST',
      body: formData,
    });
    reportResult.value = await response.json();   // triggers UI update

    // simulated
    // simulated
    // simulated
    reportResult.value
    
    console.log( reportResult.value );
    // simulated
    // simulated
    // simulated

  } catch (error) {
    console.error('Error uploading:');
    console.error( error);
  } finally {
    isLoading.value = false;    // always stop loading state
  }
};

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

        <CCardBody>
          <!-- Show placeholders only while loading -->
          <template v-if="isLoading">
            <CCardTitle v-c-placeholder="{ animation: 'glow', xs: 7 }">
              AI report: <CPlaceholder :xs="6" />
            </CCardTitle>
            <CCardText v-c-placeholder="{ animation: 'glow' }">
              <CPlaceholder :xs="7" />
              <CPlaceholder :xs="4" />
              <CPlaceholder :xs="4" />
              <CPlaceholder :xs="6" />
              <CPlaceholder :xs="8" />
              <CPlaceholder :xs="4" />
              <CPlaceholder :xs="6" />
              <CPlaceholder :xs="8" />
            </CCardText>
          </template>

          <!-- Show real content once result is available -->
          <template v-else-if="reportResult">
            <CCardTitle>AI:</CCardTitle>
            <CCardText>{{ reportResult }}</CCardText>
          </template>

          <!-- Nothing shown before upload starts -->
        </CCardBody>

        <CTable striped>
          <CTableHead>
            <CTableRow>
              <CTableHeaderCell scope="col">#</CTableHeaderCell>
              <CTableHeaderCell scope="col">Section</CTableHeaderCell>
              <CTableHeaderCell scope="col">Name</CTableHeaderCell>
              <!-- <CTableHeaderCell scope="col">Heading</CTableHeaderCell>-->
            </CTableRow>
          </CTableHead>
          <CTableBody>
            <CTableRow>
              <CTableHeaderCell scope="row">1</CTableHeaderCell>
              <CTableDataCell>Mark</CTableDataCell>
              <CTableDataCell>Otto</CTableDataCell>
              <!--
              <CTableDataCell>@mdo</CTableDataCell>
              -->
            </CTableRow>

            <CTableRow>
              <CTableHeaderCell colSpan={4}>
                <CTable>
                  <CTableHead>
                    <CTableRow>
                      <CTableHeaderCell scope="col">Section</CTableHeaderCell>
                      <CTableHeaderCell scope="col">Field</CTableHeaderCell>
                      <CTableHeaderCell scope="col">Detail</CTableHeaderCell>
                    </CTableRow>
                  </CTableHead>
                  <CTableBody>
                    <CTableRow>
                      <CTableHeaderCell scope="row">A</CTableHeaderCell>
                      <CTableDataCell>First</CTableDataCell>
                      <CTableDataCell>Last</CTableDataCell>
                    </CTableRow>
                    <CTableRow>
                      <CTableHeaderCell scope="row">B</CTableHeaderCell>
                      <CTableDataCell>First</CTableDataCell>
                      <CTableDataCell>Last</CTableDataCell>
                    </CTableRow>
                    <!--
                    <CTableRow>
                      <CTableHeaderCell scope="row">C</CTableHeaderCell>
                      <CTableDataCell>First</CTableDataCell>
                      <CTableDataCell>Last</CTableDataCell>
                    </CTableRow>
                    -->




                  </CTableBody>
                </CTable>
              </CTableHeaderCell>
            </CTableRow>
            <CTableRow>
              <CTableHeaderCell scope="row">2</CTableHeaderCell>
              <CTableDataCell colSpan={2}>Larry the Bird</CTableDataCell>
              <CTableDataCell>@twitter</CTableDataCell>
            </CTableRow>
          </CTableBody>
        </CTable>

        <CButton @click="downloadCSV" color="primary" class="mb-3">
          Save as CSV
        </CButton>

        <!--
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
        -->
    
      </CCard>
    </CCol>
  </CRow>
</template>

