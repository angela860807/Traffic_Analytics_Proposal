<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="showModal" class="overlay" @click.self="closeModal">
        <div class="modal">
          <button class="close" @click="closeModal">✕</button>

          <div class="logo">Traffic<em>AS</em></div>

          <div class="tabs">
            <button :class="{ on: modalMode === 'login' }" @click="modalMode = 'login'">
              로그인
            </button>
            <button :class="{ on: modalMode === 'signup' }" @click="modalMode = 'signup'">
              회원가입
            </button>
          </div>

          <!-- 로그인 -->
          <form v-if="modalMode === 'login'" @submit.prevent="handleLogin" class="form">
            <label
              >이메일
              <input
                v-model="email"
                type="email"
                placeholder="example@email.com"
                autocomplete="email"
              />
            </label>
            <label
              >비밀번호
              <input
                v-model="password"
                type="password"
                placeholder="비밀번호 입력"
                autocomplete="current-password"
              />
            </label>
            <p v-if="error" class="err">{{ error }}</p>
            <button type="submit" class="submit">로그인</button>
            <p class="switch">
              계정이 없으신가요? <span @click="modalMode = 'signup'">회원가입</span>
            </p>
          </form>

          <!-- 회원가입 -->
          <form v-else @submit.prevent="handleSignup" class="form">
            <label
              >이름
              <input
                v-model="name"
                type="text"
                placeholder="이름 입력"
                autocomplete="name"
              />
            </label>
            <label
              >이메일
              <input
                v-model="email"
                type="email"
                placeholder="example@email.com"
                autocomplete="email"
              />
            </label>
            <label
              >비밀번호
              <input
                v-model="password"
                type="password"
                placeholder="6자 이상"
                autocomplete="new-password"
              />
            </label>
            <label
              >비밀번호 확인
              <input
                v-model="confirm"
                type="password"
                placeholder="비밀번호 재입력"
                autocomplete="new-password"
              />
            </label>
            <p v-if="error" class="err">{{ error }}</p>
            <button type="submit" class="submit">회원가입</button>
            <p class="switch">
              이미 계정이 있으신가요? <span @click="modalMode = 'login'">로그인</span>
            </p>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from "vue";
import { useAuth } from "@/composables/useAuth";

const { showModal, modalMode, closeModal, login, signup } = useAuth();

const name = ref("");
const email = ref("");
const password = ref("");
const confirm = ref("");
const error = ref("");

watch(modalMode, () => {
  error.value = "";
  name.value = "";
  email.value = "";
  password.value = "";
  confirm.value = "";
});

const handleLogin = () => {
  error.value = "";
  if (!email.value || !password.value) {
    error.value = "이메일과 비밀번호를 입력하세요.";
    return;
  }
  try {
    login(email.value, password.value);
    closeModal();
  } catch (e) {
    error.value = e.message;
  }
};

const handleSignup = () => {
  error.value = "";
  if (!name.value || !email.value || !password.value) {
    error.value = "모든 항목을 입력하세요.";
    return;
  }
  if (password.value.length < 6) {
    error.value = "비밀번호는 6자 이상이어야 합니다.";
    return;
  }
  if (password.value !== confirm.value) {
    error.value = "비밀번호가 일치하지 않습니다.";
    return;
  }
  try {
    signup(name.value, email.value, password.value);
    closeModal();
  } catch (e) {
    error.value = e.message;
  }
};
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal {
  position: relative;
  width: 100%;
  max-width: 420px;
  background: var(--nav);
  border: 1px solid var(--b);
  border-radius: 12px;
  padding: 40px 36px 32px;
  backdrop-filter: blur(24px);
}
.close {
  position: absolute;
  top: 16px;
  right: 18px;
  background: none;
  border: none;
  color: var(--t3);
  font-size: 16px;
  cursor: pointer;
  transition: color 0.2s;
}
.close:hover {
  color: var(--t);
}

.logo {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.4px;
  color: var(--t);
  text-align: center;
  margin-bottom: 24px;
}
.logo em {
  color: var(--a);
  font-style: normal;
}

.tabs {
  display: flex;
  border: 1px solid var(--b);
  border-radius: 7px;
  overflow: hidden;
  margin-bottom: 24px;
}
.tabs button {
  flex: 1;
  padding: 9px;
  font-size: 13px;
  font-weight: 600;
  background: none;
  border: none;
  color: var(--t3);
  cursor: pointer;
  transition: all 0.2s;
}
.tabs button.on {
  background: var(--a);
  color: var(--bg);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 12px;
  color: var(--t2);
}
input {
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 13px;
  color: var(--t);
  outline: none;
  transition: border-color 0.2s;
}
input:focus {
  border-color: var(--a);
}
input::placeholder {
  color: var(--t3);
}

.err {
  font-size: 12px;
  color: #f87171;
  margin: 0;
}

.submit {
  padding: 11px;
  background: var(--a);
  color: var(--bg);
  border: none;
  border-radius: 6px;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
  margin-top: 4px;
}
.submit:hover {
  opacity: 0.87;
  transform: translateY(-1px);
}

.switch {
  font-size: 12px;
  color: var(--t3);
  text-align: center;
  margin: 0;
}
.switch span {
  color: var(--a);
  cursor: pointer;
}
.switch span:hover {
  text-decoration: underline;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.22s, transform 0.22s;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.96);
}
</style>
