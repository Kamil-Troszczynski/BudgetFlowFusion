<template>
  <main class="hero">
    <video class="hero__video" autoplay muted loop playsinline>
      <source src="/animation.mp4" type="video/mp4" />
    </video>

    <div class="hero__overlay"></div>

    <div class="hero__bottom">
      <button class="hero__link" type="button">Rozpocznij</button>

      <section class="login-sheet" aria-label="Formularz logowania">
        <div class="login-sheet__card">
          <p class="login-sheet__eyebrow">Witaj w aplikacji BudgetFlowFusion</p>
          <p class="login-sheet__description">
            Wejdź do panelu i zacznij zarządzać swoim budżetem w jednym miejscu.
          </p>

          <form class="login-sheet__form" @submit.prevent="handleSubmit">
            <label class="login-sheet__field">
              <span>E-mail</span>
              <input 
                v-model="formData.email"
                type="email" 
                placeholder="name@example.com"
                required 
              />
            </label>

            <label class="login-sheet__field">
              <span>Hasło</span>
              <input 
                v-model="formData.password"
                type="password" 
                placeholder="••••••••"
                required 
              />
            </label>

            <button class="login-sheet__submit" type="submit">Zaloguj się</button>
            <p class="login-sheet__register">
              Nie masz konta? <RouterLink to="/register">Zarejestruj się</RouterLink>
            </p>
          </form>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
  
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { login } = useAuth()

const formData = ref({
  email: '',
  password: ''
})

const handleSubmit = () => {
  login({
    firstName: 'Jan',
    lastName: 'Testowy',
    email: formData.value.email,
    circleName: 'Moja Organizacja',
    role: 'member'
  })
  
  router.push('/home')
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
}

.hero {
  position: relative;
  width: 100vw;
  height: 100dvh;
  overflow: hidden;
  background: #050816;
}

.hero__video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.05);
}

.hero__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(5, 8, 22, 0.18), rgba(5, 8, 22, 0.5));
}

.hero__bottom {
  position: fixed;
  left: 50%;
  bottom: 3.5vh;
  z-index: 2;
  display: grid;
  justify-items: center;
  width: min(100vw - 2vw, 35vw);
  transform: translateX(-50%);
  min-height: 5vh;
}

.hero__link {
  position: relative;
  z-index: 2;
  border: 0;
  border-radius: 9999px;
  padding: 1.2vw 2vw;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 1.4vw;
  font-weight: 800;
  letter-spacing: 0.03em;
  cursor: pointer;
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.38);
  transition:
    opacity 0.25s ease,
    transform 0.25s ease,
    box-shadow 0.25s ease,
    filter 0.25s ease;
}

.hero__link:hover,
.hero__link:focus-visible {
  filter: brightness(1.05);
  transform: translateY(-0.3vh);
  box-shadow: 0 18px 34px rgba(37, 99, 235, 0.5);
}

.hero__link:focus-visible {
  outline: 3px solid rgba(255, 255, 255, 0.95);
  outline-offset: 0.4vw;
  border-radius: 9999px;
}

.login-sheet {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 100%;
  opacity: 0;
  pointer-events: none;
  transform: translate(-50%, 1.5vh);
  transition:
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.35s ease;
}

.hero__bottom:hover .hero__link {
  opacity: 0;
  transform: translateY(0.8vh);
}

.hero__bottom:hover .login-sheet,
.login-sheet:hover {
  opacity: 1;
  pointer-events: auto;
  transform: translate(-50%, 0);
}

.login-sheet__card {
  padding: 2.5vw;
  border-radius: 1.8vw;
  background: rgba(9, 14, 32, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.32);
  backdrop-filter: blur(16px);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
}

.login-sheet__eyebrow {
  margin: 0 0 0.4vh;
  color: rgba(191, 219, 254, 0.96);
  font-size: 1.8vw;
  font-weight: 800;
  line-height: 1.45;
}

.login-sheet__description {
  margin: 0 0 1.5vh;
  color: rgba(226, 232, 240, 0.84);
  font-size: 1vw;
  line-height: 1.55;
}

.login-sheet__form {
  display: grid;
  gap: 1.2vw;
}

.login-sheet__field {
  display: grid;
  gap: 0.5vw;
  font-size: 1vw;
  font-weight: 700;
}

.login-sheet__field input {
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 0.95vw;
  padding: 1.1vw 1.2vw;
  background: rgba(15, 23, 42, 0.68);
  color: #ffffff;
  font: inherit;
  outline: none;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
  font-size: 0.95vw;
}

.login-sheet__field input::placeholder {
  color: rgba(226, 232, 240, 0.45);
}

.login-sheet__field input:focus {
  border-color: rgba(96, 165, 250, 0.9);
  box-shadow: 0 0 0 0.4vw rgba(59, 130, 246, 0.24);
}

.login-sheet__submit {
  margin-top: 0.3vh;
  border: none;
  border-radius: 9999px;
  padding: 1.1vw 1.5vw;
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

.login-sheet__submit:hover {
  transform: translateY(-0.3vh);
  filter: brightness(1.05);
  box-shadow: 0 18px 34px rgba(37, 99, 235, 0.5);
}

.login-sheet__submit:focus-visible {
  outline: 3px solid rgba(255, 255, 255, 0.95);
  outline-offset: 0.4vw;
}

.login-sheet__register {
  margin: 0;
  color: rgba(226, 232, 240, 0.88);
  font-size: 1vw;
  text-align: center;
}

.login-sheet__register a {
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

.login-sheet__register a:hover,
.login-sheet__register a:focus-visible {
  color: #bfdbfe;
  text-decoration: underline;
  background: rgba(59, 130, 246, 0.12);
}

@media (max-width: 640px) {
  .login-sheet__card {
    padding: 2vw;
  }
}
</style>
