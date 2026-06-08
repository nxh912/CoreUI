<template>
  <CRow>

    <CCol :xs="12">
      <CCard class="mb-4">
        <CCardHeader>
          <strong>MRO</strong> <small>upload form</small>
        </CCardHeader>
        <CCardBody>
          <DocsExample href="forms/form-control.html#file-input">

            <div class="mb-3">
              <CFormLabel for="formFileMultiple"
                >Multiple MRO files:</CFormLabel
              >
              <CFormInput id="formFileMultiple" type="file" multiple />
            </div>

          </DocsExample>
        </CCardBody>
      </CCard>
    </CCol>


  </CRow>
</template>
