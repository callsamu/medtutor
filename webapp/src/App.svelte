<script lang="ts">
  import Icon from "@iconify/svelte";
	import { fly } from "svelte/transition";
	import { Pulse } from "svelte-loading-spinners";

	interface Message {
		content: string;
		author: string;
	}

	let chatElement: HTMLDivElement;

	let chat: Message[] = [];
	let lockScroll = true;
	let question = "";
	let answerTokens: string[] = [];
	let isWritingAnswer = false;

	function toggleTheme() {
		const documentElem = document.documentElement;

		if (isDarkMode()) {
			localStorage.setItem("theme", "dark");
			documentElem.classList.remove("dark");
		} else {
			localStorage.setItem("theme", "light");
			documentElem.classList.add("dark");
		}
	}

	function isDarkMode(): boolean {
		const documentElem = document.documentElement;
		return documentElem.classList.contains("dark");
	}

	function ask(question: string) {
	  chat = [...chat, {content: question, author: "user"}];

	  const url = new URL("http://localhost:8000/debug/stream");
		url.searchParams.append("question", question);

		const source = new EventSource(url);

		source.onmessage = event => {
			const { token } = JSON.parse(event.data);

			const ce = chatElement;

			if (lockScroll) {
				ce.scrollTop = ce.scrollHeight;
			}

			answerTokens = [...answerTokens, token];
		};

		source.onerror = event => {
			console.error(event);
		}

		source.addEventListener("close", () => {
			source.close();

			isWritingAnswer = false;
			const answer = answerTokens.join("");
			chat = [...chat, {content: answer, author: "medtutor"}];
		});

		source.addEventListener("error", (event: MessageEvent) => {
			source.close();
		  isWritingAnswer = false;
			chat = [...chat, {content: event.data, author: "error"}];
			console.log(chat);
		});
	}

	function handleClick() {
		isWritingAnswer = true;
		answerTokens = [];

		ask(question);
	}

	function handleScroll() {
		const ce = chatElement;
		const currSroll = Math.floor(ce.scrollHeight - ce.offsetHeight);
		const totalScroll = Math.floor(ce.scrollTop);
		if (currSroll - totalScroll < 10) {
			lockScroll = true;
		} else {
			lockScroll = false;
		}
	}
</script>

<main>
	<button class="theme" on:click={toggleTheme}>
		<Icon icon="material-symbols:dark-mode-outline-rounded" />
	</button>

	<div bind:this={chatElement} on:scroll={handleScroll} class="chat">
		{#each chat as message}
			{#if message.author === "medtutor"}
				<div class="message medtutor-message">
					<div> 
						<img class="avatar" alt="bot" src="/bot.png" width="100"/>
					</div>
					<p class="message-text">
						{message.content}
					</p>
				</div>
			{:else if message.author === "error"}
				<div class="message error-message">
					<p style="white-space: pre-line">{message.content}</p>
				</div>
			{:else}
				<div in:fly={{ x: -20, duration: 1000 }} class="message">
					<div>
						<img class="avatar" alt="user" src="/user.png" width="100"/>
					</div>
					<p class="message-text">
						{message.content}
					</p>
				</div>
			{/if}
		{/each}
	
		{#if isWritingAnswer}
			<div in:fly={{ x: -20, duration: 1000, delay: 1000 }} 
					 class="message medtutor-message answer">
				<div>
					<img class="avatar" alt="bot" src="/bot.png" width="100">
				</div>
				<p class="message-text">
					{#if answerTokens.length === 0}
						<div class="loading">
							<Pulse 
								size="40" 
								color={isDarkMode() ? "#6b7280" : "#94a3b8"} />
						</div>
					{:else}
						{#each answerTokens as token, i}
							{#if (i === answerTokens.length - 1)  && isWritingAnswer}
								<span class="current-token">{token}</span>
							{:else} 
								{token}
							{/if}
						{/each}
					{/if}
				</p>
			</div>
		{/if}
	</div>

	<div class="prompt">
		<form on:submit|preventDefault={handleClick}>
			<div bind:innerText={question} class="text-box" contenteditable="true"></div>
			{#if !isWritingAnswer && question.trim().length > 0 }
			<button class="send" type="submit">
				<Icon icon="fluent:send-24-filled" style="font-size: 2rem" />
			</button>
			{/if}
		</form>
	</div>
</main>

<style>
main {
	height: 100%;
	width: 100%;
	background-color: var(--bg-1);
}

.theme {
	top: 1rem;
	right: 1rem;
	position: fixed;
	display: flex;
	vertical-align: center;
	border: 2px solid var(--fg-2);
	background-color: rgba(0, 0, 0, 0);
	border-radius: 3rem;
	color: var(--fg-2);
	cursor: pointer;
	font-size: 30px;
	position: fixed;
}

.chat {
	top: 0;
	height: 90%;
	width: 100%;
	margin: 0 auto;
	overflow-y: scroll;
	font-size: 1rem;
	color: var(--fg-1);
}

.loading {
	margin: 0 0.25rem;
	display: inline-block;
	vertical-align: center;
}

.avatar {
	border-radius: 0.25rem;
}

.message {
	display: flex;
	justify-content: center;
	padding: 1rem;
}

.message > p {
	margin: 0.25rem 2rem;
	width: 40%;
}

.medtutor-message {
	background-color: var(--bg-2);
	border-top: 1px solid var(--border);
	border-bottom: 1px solid var(--border);
}

.error-message {
	background-color: var(--error);
}

.message-text {
	white-space: pre-wrap;
}

.current-token {
	padding-right: 0.2rem;
	border-right: 0.5rem solid #64748b;
}

.prompt {
	position: fixed;
	left: 0;
	bottom: 1rem;
	width: 100%;
	height: auto;
	text-align: center;
}

form {
	width: 40%;
	height: auto;
	margin: 0 auto;
	padding: 0.5rem;
	color: var(--fg-1);
	background-color: var(--bg-3);
	border: 2px solid var(--border);
	border-radius: 0 0.75rem 0.75rem 0.75rem;
	display: flex;
	align-items: center;
	justify-content: space-between;
	box-shadow: 2.5px 2.5px 5px rgba(0, 0, 0, 0.5);
}

.text-box {
	border: none;
	outline: none;
	word-wrap: break-word;
	text-align: left;
	
	min-width: 90%;
	padding: 0.5rem;
	font-size: 1rem;
	display: inline-block;
}

.send {
	display: flex;
	align-items: center;
	justify-content: center;
	background-color: var(--green);
	border-radius: 0.5rem;
	font-weight: 600;
	color: white;
  border: none;
	cursor: pointer;
}
</style>
