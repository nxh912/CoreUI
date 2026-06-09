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
  alert(2);

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

        <table class="table">
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
              <td>Larry</td>
              <td>the Bird</td>
              <td>@twitter</td>
            </tr>
          </tbody>
        </table>
        <CContainer>
          <CRow>
            <CCol>1 of 3</CCol>
            <CCol xs={6}>2 of 3 (wider)</CCol>
            <CCol>3 of 3</CCol>
          </CRow>
          <CRow>
            <CCol>1 of 3</CCol>
            <CCol xs={6}>2 of 3 (wider)</CCol>
            <CCol>3 of 3</CCol>
          </CRow>
        </CContainer>

      </CCard>
    </CCol>
  </CRow>
</template>
