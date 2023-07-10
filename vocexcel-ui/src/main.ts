import './assets/main.css'
//theme
import 'primevue/resources/themes/lara-light-blue/theme.css'
//core
import 'primevue/resources/primevue.min.css'
//icons
import 'primeicons/primeicons.css'

import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)
app.use(PrimeVue)
app.use(ToastService)

app.mount('#app')
