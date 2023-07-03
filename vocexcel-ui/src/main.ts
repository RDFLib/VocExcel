import './assets/main.css'
//theme
import 'primevue/resources/themes/lara-light-blue/theme.css'
//core
import 'primevue/resources/primevue.min.css'

import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import Button from 'primevue/button'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)
app.use(PrimeVue)

app.component('Button', Button)

app.mount('#app')
