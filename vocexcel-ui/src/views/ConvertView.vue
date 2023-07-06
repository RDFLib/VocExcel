<script setup lang="ts">
import { ref } from 'vue'
import FileUpload from 'primevue/fileupload'
import { type FileUploadUploadEvent, type FileUploadErrorEvent } from 'primevue/fileupload'
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import Button from 'primevue/button'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

import VocabTree from '@/components/VocabTree.vue'

const toast = useToast()
const rdfTurtle = ref('')
const copyButtonTextDefault = 'Copy result'
const copyButtonTextCopied = 'Copied!'
const ONE_SECOND_IN_MS = 1000
const copyButtonText = ref(copyButtonTextDefault)
const previewWidth = ref(0)

const onUploadComplete = (event: FileUploadUploadEvent) => {
  rdfTurtle.value = event.xhr.response
}

const onError = (event: FileUploadErrorEvent) => {
  let filename = null
  if (Array.isArray(event.files)) {
    filename = event.files[0].name
  } else {
    filename = event.files
  }

  const errorMsg = `Failed to upload file ${filename}`
  console.error(errorMsg)
  toast.add({
    severity: 'error',
    summary: 'Error',
    detail: errorMsg,
    life: 3000
  })
}

const handleCopyRdfTurtle = () => {
  navigator.clipboard.writeText(rdfTurtle.value).then(
    () => {
      copyButtonText.value = copyButtonTextCopied
      setTimeout(() => {
        copyButtonText.value = copyButtonTextDefault
      }, ONE_SECOND_IN_MS)
    },
    () => {
      const errorMsg = 'Error copying result to clipboard'
      console.error(errorMsg)
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: errorMsg,
        life: 3000
      })
    }
  )
}
</script>

<template>
  <main>
    <h1>Convert</h1>
    <p>
      Currently supported VocExcel template file is 0.6.2. Download the template files
      <a target="_blank" href="https://github.com/RDFLib/VocExcel/tree/master/templates">here</a>.
    </p>
    <p>Select a VocExcel file and upload it to convert it to a SKOS vocabulary.</p>

    <Toast />
    <FileUpload
      name="upload_file"
      url="http://localhost:8000/api/v1/convert"
      :multiple="false"
      accept=".xlsx"
      :maxFileSize="1000000"
      :preview-width="previewWidth"
      @upload="onUploadComplete"
      @error="onError"
    >
      <template #empty>
        <p>Drag and drop files to here to upload.</p>
      </template>
    </FileUpload>

    <div v-if="rdfTurtle">
      <VocabTree :rdf-turtle="rdfTurtle" />

      <Accordion class="mt-4">
        <AccordionTab header="Total RDF Turtle result">
          <div class="flex flex-row-reverse">
            <Button @click="handleCopyRdfTurtle" size="small"
              ><span class="pr-2">{{ copyButtonText }}</span> <i class="pi pi-copy"></i
            ></Button>
          </div>

          <pre>{{ rdfTurtle }}</pre>
        </AccordionTab>
      </Accordion>
    </div>

    <div class="mt-4">
      <router-link to="/" class="no-underline">
        <Button size="small" severity="info" outlined>Back to home</Button>
      </router-link>
    </div>
  </main>
</template>
