<template>
  <main class="hero">
    <div class="hero__overlay"></div>

    <div class="hero__content">
      <section class="signup-section" aria-label="Formularz rejestracji">
        <div class="signup-card__header">
          <p class="signup-card__eyebrow">Utwórz konto</p>
          <p class="signup-card__description">
            Dołącz do BudgetFlowFusion i zacznij zarządzać swoim budżetem.
          </p>
        </div>

        <form class="signup-form" @submit.prevent="handleSubmit">
          <label class="signup-form__field">
            <span>Imię</span>
            <input 
              v-model="formData.firstName"
              type="text" 
              placeholder="Jan" 
              required
            />
          </label>

          <label class="signup-form__field">
            <span>Nazwisko</span>
            <input 
              v-model="formData.lastName"
              type="text" 
              placeholder="Kowalski" 
              required
            />
          </label>

          <label class="signup-form__field">
            <span>E-mail</span>
            <input 
              v-model="formData.email"
              type="email" 
              placeholder="name@example.com" 
              required
            />
          </label>

          <label class="signup-form__field">
            <span>Nazwa koła</span>
            <input 
              v-model="formData.circleName"
              type="text" 
              placeholder="Moja organizacja" 
              required
            />
          </label>

          <label class="signup-form__field">
            <span>Hasło</span>
            <input 
              v-model="formData.password"
              type="password" 
              placeholder="••••••••" 
              required
            />
          </label>

          <label class="signup-form__field">
            <span>Potwierdź hasło</span>
            <input 
              v-model="formData.confirmPassword"
              type="password" 
              placeholder="••••••••" 
              required
            />
          </label>

          <div class="signup-form__role-toggle">
            <span class="signup-form__role-label">Rola</span>
            <button 
              class="signup-form__toggle" 
              :class="{ 'is-treasurer': formData.role === 'treasurer' }"
              type="button"
              @click="toggleRole"
            >
              <span class="signup-form__toggle-text">
                {{ formData.role === 'member' ? 'Zwykły członek koła' : 'Skarbnik' }}
              </span>
              <span class="signup-form__toggle-indicator"></span>
            </button>
          </div>

          <button class="signup-form__submit" type="submit">Zarejestruj się</button>

          <p class="signup-form__register">
            Masz już konto? <RouterLink to="/login">Zaloguj się</RouterLink>
          </p>
        </form>
      </section>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { register } = useAuth()

const formData = ref({
  firstName: '',
  lastName: '',
  email: '',
  circleName: '',
  password: '',
  confirmPassword: '',
  role: 'member'
})

const handleSubmit = () => {
  if (formData.value.password !== formData.value.confirmPassword) {
    alert('Hasła nie są identyczne!')
    return
  }
  
  register(formData.value)
  router.push('/home')
}

const toggleRole = () => {
  formData.value.role = formData.value.role === 'member' ? 'treasurer' : 'member'
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800&display=swap');

:global(html),
:global(body),
:global(#app) {
  width: 100%;
  height: 100%;
  margin: 0;
  overflow-x: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

:global(html::-webkit-scrollbar),
:global(body::-webkit-scrollbar),
:global(#app::-webkit-scrollbar) {
  display: none;
  width: 0;
  height: 0;
}

.hero {
  position: relative;
  width: 100%;
  min-height: 100dvh;
  background: #050816;
  overflow-y: scroll;
  overflow-x: hidden;
  scroll-behavior: smooth;
  scrollbar-width: none;
  -ms-overflow-style: none;
  font-family: 'Nunito', system-ui, sans-serif;
}

.hero::-webkit-scrollbar {
  display: none;
}

.hero::-webkit-scrollbar {
  display: none;
}

.hero__overlay {
  position: fixed;
  inset: 0;
  background: linear-gradient(180deg, rgba(5, 8, 22, 0.18), rgba(5, 8, 22, 0.5));
  pointer-events: none;
  z-index: 1;
}

.hero__content {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  padding: 2vh 3vw;
  box-sizing: border-box;
}

.signup-section {
  width: 100%;
  max-width: 40vw;
  padding: 0;
}

.signup-card__header {
  margin-bottom: 2.5vh;
}

.signup-card__eyebrow {
  margin: 0 0 0.8vh;
  color: rgba(191, 219, 254, 0.96);
  font-size: 2.2vw;
  font-weight: 800;
  line-height: 1.45;
  font-family: 'Nunito', system-ui, sans-serif;
}

.signup-card__description {
  margin: 0;
  color: rgba(226, 232, 240, 0.84);
  font-size: 1vw;
  line-height: 1.55;
  font-family: 'Nunito', system-ui, sans-serif;
}

.signup-form {
  display: grid;
  gap: 1.5vw;
  font-family: 'Nunito', system-ui, sans-serif;
}

.signup-form__field {
  display: grid;
  gap: 0.5vw;
  font-size: 1vw;
  font-weight: 700;
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
}

.signup-form__field input {
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 0.9vw;
  padding: 1.2vw 1.3vw;
  background: rgba(15, 23, 42, 0.68);
  color: #ffffff;
  font: inherit;
  outline: none;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 0.95vw;
}

.signup-form__field input::placeholder {
  color: rgba(226, 232, 240, 0.45);
}

.signup-form__field input:focus {
  border-color: rgba(96, 165, 250, 0.9);
  box-shadow: 0 0 0 0.4vw rgba(59, 130, 246, 0.24);
}

.signup-form__roles {
  display: flex;
  flex-direction: row;
  gap: 2vw;
}

.signup-form__radio {
  display: flex;
  align-items: center;
  gap: 0.9vw;
  cursor: pointer;
  font-weight: 500;
  font-size: 1vw;
  font-family: 'Nunito', system-ui, sans-serif;
}

.signup-form__radio input[type="radio"] {
  width: 1.2vw;
  height: 1.2vw;
  cursor: pointer;
  accent-color: #3b82f6;
  flex-shrink: 0;
}

fieldset {
  border: none;
  padding: 0;
  margin: 0;
}

fieldset legend {
  font-weight: 700;
  font-size: 1vw;
  margin-bottom: 0.6vh;
  padding: 0;
  font-family: 'Nunito', system-ui, sans-serif;
}

.signup-form__role-toggle {
  display: flex;
  flex-direction: column;
  gap: 0.6vw;
}

.signup-form__role-label {
  font-weight: 700;
  font-size: 1vw;
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
}

.signup-form__toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.9vw 1.2vw;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 0.9vw;
  background: rgba(15, 23, 42, 0.68);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 1vw;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.signup-form__toggle:hover {
  border-color: rgba(96, 165, 250, 0.5);
  background: rgba(15, 23, 42, 0.85);
}

.signup-form__toggle.is-treasurer {
  border-color: rgba(96, 165, 250, 0.9);
  background: rgba(59, 130, 246, 0.15);
}

.signup-form__toggle-text {
  flex: 1;
  text-align: left;
}

.signup-form__toggle-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5vw;
  height: 1.5vw;
  margin-left: 0.8vw;
  border-radius: 0.4vw;
  background: rgba(96, 165, 250, 0.3);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.signup-form__toggle.is-treasurer .signup-form__toggle-indicator {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.signup-form__toggle-indicator::after {
  content: '↔';
  color: #ffffff;
  font-size: 0.95vw;
  font-weight: bold;
}

.signup-form__submit {
  margin-top: 0.8vh;
  border: none;
  border-radius: 9999vw;
  padding: 1.2vw 1.8vw;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 1.4vw;
  font-weight: 800;
  letter-spacing: 0.02em;
  cursor: pointer;
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.38);
  transition: 
    transform 0.2s ease,
    box-shadow 0.2s ease,
    filter 0.2s ease;
}

.signup-form__submit:hover {
  transform: translateY(-0.3vh);
  filter: brightness(1.05);
  box-shadow: 0 18px 34px rgba(37, 99, 235, 0.5);
}

.signup-form__submit:focus-visible {
  outline: 3px solid rgba(255, 255, 255, 0.95);
  outline-offset: 0.4vw;
}

.signup-form__register {
  margin: 0;
  color: rgba(226, 232, 240, 0.88);
  font-size: 1vw;
  text-align: center;
  padding-bottom: 2vh;
  font-family: 'Nunito', system-ui, sans-serif;
}

.signup-form__register a {
  display: inline-block;
  padding: 0.6vw 0.9vw;
  color: #93c5fd;
  font-weight: 800;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 1.1vw;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 0.5vw;
}

.signup-form__register a:hover,
.signup-form__register a:focus-visible {
  color: #bfdbfe;
  text-decoration: underline;
  background: rgba(59, 130, 246, 0.12);
}

@media (max-width: 768px) {
  .signup-form__roles {
    flex-direction: column;
    gap: 0.9vw;
  }
}
</style>
