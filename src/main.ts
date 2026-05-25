import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { useAuth } from './composables/useAuth'

const app = createApp(App)
app.mount('#app')

const { fetchMe } = useAuth()
fetchMe()
