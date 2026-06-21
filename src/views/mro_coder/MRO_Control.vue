<script setup>
import { ref } from 'vue';

const files = ref(null);
const isLoading = ref(false);       // tracks whether upload is in progress
const reportResult = ref(null);     // stores the API response

const handleFileChange = (event) => {
  files.value = event.target.files;
};

const uploadFiles = async () => {
  if (!files.value || files.value.length === 0) return;

  isLoading.value = true;
  reportResult.value = null;

  try {
    const file = files.value[0];
    
    // Read the text lines from the uploaded report file inside the browser
    const fileContent = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(e);
      reader.readAsText(file);
    });

    // Format a compliant JSON request payload that matches server2.py's structural definition
    const jsonPayload = {
      instruction: "Review the clinical scenario and prioritize calculations based on instructions.",
      context: fileContent, // Pass the extracted text content of the report verbatim
      temperature: 0.7
    };

    // Fire the request with the native application/json Content-Type header
    const response = await fetch("http://127.0.0.1:8000/api/v1/mro_data", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(jsonPayload),
    });

    var jsonobj = await response.json();
    console.log("jsonobj return from BEDROCK...")
    console.log(jsonobj)
  
    if (jsonobj && typeof jsonobj === 'object') {

      if ('detail' in jsonobj) {
        console.log("Validation details:", jsonobj['detail']);
        reportResult.value = JSON.stringify(jsonobj['detail'], null, 2);

      } else {
        let outputText = jsonobj.output || jsonobj.result || JSON.stringify(jsonobj);
        if (typeof outputText === 'string') {
          outputText = outputText.replaceAll("\\n", "\n");
        }
        reportResult.value = outputText;
      }
      
    } else {
      reportResult.value = "Network error E61: Received an empty or invalid response.";
    }
  } catch (error) {
    reportResult.value = "Network error E64: " + error.toString();
    console.error("Network error during processing sequence:", error);
  } finally {
    isLoading.value = false;
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

          <!-- Show real content once result is available
          <template v-else-if="reportResult">
            <CCardTitle>AI:</CCardTitle>
            <CCardText>{{ reportResult }}</CCardText>
          </template>
          -->

          <!-- Nothing shown before upload starts -->
        </CCardBody>

        <CTable striped>
          <textarea 
            class="form-control" 
            id="AIOutput" 
            rows="20" 
            v-model="reportResult"
          ></textarea>
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

