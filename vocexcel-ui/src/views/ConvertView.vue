<script setup lang="ts">
import { ref } from 'vue'
import FileUpload from 'primevue/fileupload'
import { type FileUploadUploadEvent } from 'primevue/fileupload'

const rdfTurtle = ref('')
const copyButtonTextDefault = 'Copy result'
const copyButtonTextCopied = 'Copied!'
const ONE_SECOND_IN_MS = 1000
const copyButtonText = ref(copyButtonTextDefault)

const onUploadComplete = (event: FileUploadUploadEvent) => {
  rdfTurtle.value = event.xhr.response
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
      console.error('Error copying result to clipboard')
    }
  )
}
</script>

<template>
  <main>
    <h1>Convert</h1>
    <p>Select a VocExcel file and upload it to convert it to a SKOS vocabulary.</p>
    <FileUpload
      name="upload_file"
      url="http://localhost:8000/convert"
      :multiple="false"
      accept=".xlsx"
      :maxFileSize="1000000"
      @upload="onUploadComplete"
    >
      <template #empty>
        <p>Drag and drop files to here to upload.</p>
      </template>
    </FileUpload>

    <div v-if="rdfTurtle">
      <div class="flex justify-between items-end">
        <h3>Result</h3>
        <div class="flex-shrink-0">
          <Button @click="handleCopyRdfTurtle" size="small">{{ copyButtonText }}</Button>
        </div>
      </div>

      <pre>{{ rdfTurtle }}</pre>
    </div>

    <div class="mt-4">
      <router-link to="/" class="no-underline">
        <Button size="small">Back to home</Button>
      </router-link>
    </div>
  </main>
</template>
