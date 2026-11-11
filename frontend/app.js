const API_BASE_URL = "http://127.0.0.1:8000";
const chatForm = document.querySelector("#chat-form");
const messageInput = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const conversation = document.querySelector("#conversation");
const messages = document.querySelector("#messages");
const welcome = document.querySelector("#welcome");
const newChatButtons = document.querySelectorAll("#new-chat, #mobile-new-chat");
const connectionStatus = document.querySelector("#connection-status");
const statusDot = document.querySelector("#status-dot");
const toolTabs = document.querySelectorAll(".tool-tab");
const chatView = document.querySelector("#chat-view");
const toolViews = {
  quiz: document.querySelector("#quiz-view"),
  flashcards: document.querySelector("#flashcards-view"),
  summarize: document.querySelector("#summarize-view"),
};

function setConnectionStatus(online) {
  connectionStatus.textContent = online ? "Assistant is online" : "Can't reach the assistant";
  statusDot.classList.toggle("is-online", online);
  statusDot.classList.toggle("is-offline", !online);
}

function scrollToLatest() {
  conversation.scrollTo({ top: conversation.scrollHeight, behavior: "smooth" });
}

function appendMessage(role, text, metaText = "") {
  const message = document.createElement("article");
  message.className = `message ${role}`;

  const avatar = document.createElement("span");
  avatar.className = "message-avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = role === "assistant" ? "✦" : "You";

  const content = document.createElement("div");
  content.className = "message-content";
  content.textContent = text;

  if (metaText) {
    const meta = document.createElement("div");
    meta.className = "message-meta";
    meta.textContent = metaText;
    content.append(meta);
  }

  message.append(avatar, content);
  messages.append(message);
  scrollToLatest();
  return message;
}

function showTypingIndicator() {
  const message = document.createElement("article");
  message.className = "message assistant";
  message.setAttribute("aria-label", "Assistant is responding");

  const avatar = document.createElement("span");
  avatar.className = "message-avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = "✦";

  const bubble = document.createElement("div");
  bubble.className = "message-content";
  const indicator = document.createElement("span");
  indicator.className = "typing-indicator";
  indicator.setAttribute("aria-hidden", "true");

  for (let index = 0; index < 3; index += 1) {
    indicator.append(document.createElement("span"));
  }

  bubble.append(indicator);
  message.append(avatar, bubble);
  messages.append(message);
  scrollToLatest();
  return message;
}

function getErrorMessage(body, status) {
  if (typeof body?.detail === "string") {
    return body.detail;
  }
  if (Array.isArray(body?.detail)) {
    return body.detail.map((item) => item.msg).filter(Boolean).join(" ");
  }
  if (typeof body?.message === "string") {
    return body.message;
  }
  return `The request failed (HTTP ${status}). Please try again.`;
}

async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    setConnectionStatus(response.ok);
  } catch (error) {
    setConnectionStatus(false);
    console.error("Could not check the assistant API health.", error);
  }
}

async function sendMessage(message) {
  appendMessage("user", message);
  welcome.hidden = true;
  messageInput.value = "";
  messageInput.style.height = "auto";
  sendButton.disabled = true;
  const typingMessage = showTypingIndicator();

  try {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const body = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(getErrorMessage(body, response.status));
    }

    if (typeof body?.answer !== "string") {
      throw new Error("The assistant returned an unexpected response. Please try again.");
    }

    typingMessage.remove();
    const tokenInfo = Number.isFinite(body.tokens_used) ? ` · ${body.tokens_used} tokens` : "";
    appendMessage("assistant", body.answer, `${body.model || "AI Assistant"}${tokenInfo}`);
    setConnectionStatus(true);
  } catch (error) {
    typingMessage.remove();
    const messageText = error instanceof TypeError
      ? "Unable to connect to the assistant. Check that the backend is running, then try again."
      : error.message;
    appendMessage("assistant", messageText);
    setConnectionStatus(false);
    console.error("Could not send a message to the assistant.", error);
  } finally {
    sendButton.disabled = false;
    messageInput.focus();
  }
}

function showTool(viewName) {
  chatView.hidden = viewName !== "chat";
  Object.entries(toolViews).forEach(([name, view]) => {
    view.hidden = name !== viewName;
  });
  toolTabs.forEach((tab) => {
    const active = tab.dataset.view === viewName;
    tab.classList.toggle("is-active", active);
    if (active) {
      tab.setAttribute("aria-current", "page");
    } else {
      tab.removeAttribute("aria-current");
    }
  });
}

function appendResultsHeading(container, title, detail) {
  const heading = document.createElement("div");
  heading.className = "results-heading";
  const titleElement = document.createElement("h2");
  titleElement.textContent = title;
  const detailElement = document.createElement("span");
  detailElement.textContent = detail;
  heading.append(titleElement, detailElement);
  container.append(heading);
}

async function submitToolForm({ form, endpoint, errorElement, results, getPayload, render }) {
  const submitButton = form.querySelector('button[type="submit"]');
  errorElement.hidden = true;
  errorElement.textContent = "";
  results.replaceChildren();
  results.textContent = "Working on it…";
  submitButton.disabled = true;
  form.setAttribute("aria-busy", "true");

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getPayload(new FormData(form))),
    });
    const body = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(getErrorMessage(body, response.status));
    }

    results.replaceChildren();
    render(body, results);
  } catch (error) {
    results.replaceChildren();
    errorElement.textContent = error instanceof TypeError
      ? "Unable to connect to the assistant. Check that the backend is running, then try again."
      : error.message;
    errorElement.hidden = false;
    console.error(`Request to ${endpoint} failed.`, error);
  } finally {
    submitButton.disabled = false;
    form.removeAttribute("aria-busy");
  }
}

function renderQuiz(body, container) {
  if (!Array.isArray(body?.quizz) || body.quizz.length === 0) {
    throw new Error("The assistant returned an unexpected quiz. Please try again.");
  }

  appendResultsHeading(container, body.topic || "Your quiz", `${body.quizz.length} questions`);
  const questionCards = [];

  body.quizz.forEach((question, index) => {
    if (typeof question?.question !== "string" || !Array.isArray(question.options)) {
      throw new Error("The assistant returned an incomplete quiz. Please try again.");
    }

    const card = document.createElement("article");
    card.className = "quiz-question";
    const title = document.createElement("h3");
    title.textContent = `${index + 1}. ${question.question}`;
    const options = document.createElement("fieldset");
    options.className = "quiz-options";
    options.setAttribute("aria-label", `Answers for question ${index + 1}`);

    question.options.forEach((option, optionIndex) => {
      const label = document.createElement("label");
      label.className = "quiz-option";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = `quiz-question-${index}`;
      input.value = String(option);
      const text = document.createElement("span");
      text.textContent = String(option);
      label.append(input, text);
      options.append(label);
    });

    const feedback = document.createElement("p");
    feedback.className = "quiz-feedback";
    feedback.setAttribute("aria-live", "polite");
    card.append(title, options, feedback);
    container.append(card);
    questionCards.push({ card, question, feedback });
  });

  const checkButton = document.createElement("button");
  checkButton.className = "primary-button results-action";
  checkButton.type = "button";
  checkButton.textContent = "Check answers";
  checkButton.addEventListener("click", () => {
    let score = 0;
    questionCards.forEach(({ card, question, feedback }) => {
      const correctAnswer = String(question.correct ?? "");
      const options = card.querySelectorAll(".quiz-option");
      const selected = card.querySelector('input[type="radio"]:checked');

      options.forEach((option) => {
        const input = option.querySelector("input");
        option.classList.toggle("is-correct", input.value === correctAnswer);
        option.classList.toggle("is-incorrect", input.checked && input.value !== correctAnswer);
      });

      if (selected?.value === correctAnswer) {
        score += 1;
        feedback.textContent = "Correct!";
        feedback.className = "quiz-feedback is-correct";
      } else {
        feedback.textContent = selected
          ? `Not quite. The correct answer is ${correctAnswer}.`
          : `No answer selected. The correct answer is ${correctAnswer}.`;
        feedback.className = "quiz-feedback is-incorrect";
      }
    });
    checkButton.textContent = `Score: ${score} / ${questionCards.length}`;
  });
  container.append(checkButton);
}

function renderFlashcards(body, container) {
  if (!Array.isArray(body?.flashcards) || body.flashcards.length === 0) {
    throw new Error("The assistant returned no flashcards. Please try again.");
  }

  appendResultsHeading(container, body.topic || "Your flashcards", "Select a card to reveal its answer");
  body.flashcards.forEach((card, index) => {
    if (typeof card?.front !== "string" || typeof card?.back !== "string") {
      throw new Error("The assistant returned an incomplete flashcard set. Please try again.");
    }
    const element = document.createElement("details");
    element.className = "flashcard";
    const question = document.createElement("summary");
    question.textContent = `${index + 1}. ${card.front}`;
    const answer = document.createElement("p");
    answer.className = "flashcard-answer";
    answer.textContent = card.back;
    element.append(question, answer);
    container.append(element);
  });
}

function renderSummary(body, container) {
  if (!Array.isArray(body?.summary) || body.summary.length === 0) {
    throw new Error("The assistant returned an empty summary. Please try again.");
  }

  const card = document.createElement("article");
  card.className = "summary-card";
  const wordCount = Number.isFinite(body.word_count) ? `${body.word_count} words in source` : "";
  appendResultsHeading(card, "Key takeaways", wordCount);
  const list = document.createElement("ul");
  list.className = "summary-list";
  body.summary.forEach((point) => {
    const item = document.createElement("li");
    item.textContent = String(point);
    list.append(item);
  });
  card.append(list);
  container.append(card);
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message || sendButton.disabled) {
    return;
  }
  sendMessage(message);
});

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

messageInput.addEventListener("input", () => {
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 140)}px`;
});

document.querySelectorAll(".suggestion").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.prompt || "";
    messageInput.focus();
    messageInput.dispatchEvent(new Event("input"));
  });
});

toolTabs.forEach((tab) => {
  tab.addEventListener("click", () => showTool(tab.dataset.view));
});

newChatButtons.forEach((button) => button.addEventListener("click", () => {
  showTool("chat");
  messages.replaceChildren();
  welcome.hidden = false;
  messageInput.value = "";
  messageInput.style.height = "auto";
  messageInput.focus();
}));

document.querySelector("#quiz-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  submitToolForm({
    form,
    endpoint: "/quizz/",
    errorElement: document.querySelector("#quiz-error"),
    results: document.querySelector("#quiz-results"),
    getPayload: (data) => ({
      subject: data.get("subject").trim(),
      number_quizzes: Number(data.get("number_quizzes")),
      number_options: Number(data.get("number_options")),
    }),
    render: renderQuiz,
  });
});

document.querySelector("#flashcards-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  submitToolForm({
    form,
    endpoint: "/flashcard/",
    errorElement: document.querySelector("#flashcards-error"),
    results: document.querySelector("#flashcards-results"),
    getPayload: (data) => ({
      topic: data.get("topic").trim(),
      number_flashcards: Number(data.get("number_flashcards")),
    }),
    render: renderFlashcards,
  });
});

document.querySelector("#summarize-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  submitToolForm({
    form,
    endpoint: "/summarize/",
    errorElement: document.querySelector("#summarize-error"),
    results: document.querySelector("#summarize-results"),
    getPayload: (data) => ({
      text: data.get("text").trim(),
      max_bullets: Number(data.get("max_bullets")),
    }),
    render: renderSummary,
  });
});

checkHealth();
