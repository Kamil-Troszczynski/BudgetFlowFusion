<template>
  <main class="hero">
    <!-- Choose instead uncommented line in order to hear mp4 -->
    <!-- <video class="hero__video" autoplay controls loop playsinline> -->
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

          <form class="login-sheet__form">
            <label class="login-sheet__field">
              <span>E-mail</span>
              <input type="email" placeholder="name@example.com" />
            </label>

            <label class="login-sheet__field">
              <span>Hasło</span>
              <input type="password" placeholder="••••••••" />
            </label>

            <button class="login-sheet__submit" type="button">Zaloguj się</button>
            <p class="login-sheet__register">
              Nie masz konta? <a href="#">Zarejestruj się</a>
            </p>
          </form>
        </div>
      </section>
    </div>
  </main>
</template>

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
  bottom: 3.7rem;
  z-index: 2;
  display: grid;
  justify-items: center;
  width: min(100vw - 1.5rem, 560px);
  transform: translateX(-50%);
  min-height: 4rem;
}

.hero__link {
  position: relative;
  z-index: 2;
  border: 0;
  border-radius: 9999px;
  padding: 0.95rem 1.5rem;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 1.4rem;
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
  transform: translateY(-2px);
  box-shadow: 0 18px 34px rgba(37, 99, 235, 0.5);
}

.hero__link:focus-visible {
  outline: 3px solid rgba(255, 255, 255, 0.95);
  outline-offset: 4px;
  border-radius: 9999px;
}

.login-sheet {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 100%;
  opacity: 0;
  pointer-events: none;
  transform: translate(-50%, 18px);
  transition:
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.35s ease;
}

.hero__bottom:hover .hero__link {
  opacity: 0;
  transform: translateY(8px);
}

.hero__bottom:hover .login-sheet,
.login-sheet:hover {
  opacity: 1;
  pointer-events: auto;
  transform: translate(-50%, 0);
}

.login-sheet__card {
  padding: 2rem;
  border-radius: 1.75rem;
  background: rgba(9, 14, 32, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.32);
  backdrop-filter: blur(16px);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
}

.login-sheet__eyebrow {
  margin: 0 0 0.35rem;
  color: rgba(191, 219, 254, 0.96);
  font-size: 1.79rem;
  font-weight: 800;
  line-height: 1.45;
}

.login-sheet__description {
  margin: 0 0 1.5rem;
  color: rgba(226, 232, 240, 0.84);
  line-height: 1.55;
}

.login-sheet__form {
  display: grid;
  gap: 1rem;
}

.login-sheet__field {
  display: grid;
  gap: 0.45rem;
  font-size: 0.95rem;
  font-weight: 700;
}

.login-sheet__field input {
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 0.95rem;
  padding: 0.95rem 1rem;
  background: rgba(15, 23, 42, 0.68);
  color: #ffffff;
  font: inherit;
  outline: none;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.login-sheet__field input::placeholder {
  color: rgba(226, 232, 240, 0.45);
}

.login-sheet__field input:focus {
  border-color: rgba(96, 165, 250, 0.9);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.24);
}

.login-sheet__submit {
  margin-top: 0.25rem;
  border: none;
  border-radius: 9999px;
  padding: 0.95rem 1.25rem;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 1.4rem;
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
  transform: translateY(-2px);
  filter: brightness(1.05);
  box-shadow: 0 18px 34px rgba(37, 99, 235, 0.5);
}

.login-sheet__submit:focus-visible {
  outline: 3px solid rgba(255, 255, 255, 0.95);
  outline-offset: 4px;
}

.login-sheet__register {
  margin: 0;
  color: rgba(226, 232, 240, 0.88);
  font-size: 0.96rem;
  text-align: center;
}

.login-sheet__register a {
  color: #93c5fd;
  font-weight: 800;
  text-decoration: none;
}

.login-sheet__register a:hover,
.login-sheet__register a:focus-visible {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .login-sheet__card {
    padding: 1.5rem;
  }
}
</style>
