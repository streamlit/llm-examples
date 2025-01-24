document.getElementById('send-button').onclick = function() {
    var userInput = document.getElementById('user-input').value;
    if (userInput.trim() !== "") {
        addMessage(userInput, 'user-message');
        document.getElementById('user-input').value = '';
        setTimeout(() => {
            addMessage(getBotResponse(userInput), 'bot-message');
        }, 1000);
    }
};

function addMessage(message, className) {
    var chatBox = document.getElementById('chat-box');
    var messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message ' + className;
    messageDiv.textContent = message;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight; 
}

function getBotResponse(userInput) {

    if (userInput.toLowerCase().includes("hello")) {
        return "Hi there! How can I assist you?";
    } else if (userInput.toLowerCase().includes("how are you")) {
        return "I'm just a bot, but thanks for asking!";
    } else {
        return "Sorry, I didn't understand that.";
    }
}


const stars = document.querySelectorAll('.star');
const feedbackMessage = document.getElementById('feedback-message');

stars.forEach(star => {
    star.addEventListener('click', () => {
        const ratingValue = star.getAttribute('data-value');
        
        stars.forEach(s => s.classList.remove('selected'));
        
        for (let i = 0; i < ratingValue; i++) {
            stars[i].classList.add('selected');
        }

        feedbackMessage.textContent = `Você avaliou com ${ratingValue} estrela(s)!`;
    });
});



/* Lulu chat bot*/
// Função para adicionar a mensagem ao histórico
function addMessageToHistory(message, sender) {
    const chatHistory = document.getElementById('chat-history');
  
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageDiv.innerText = message;
  
    chatHistory.appendChild(messageDiv);
    
    // Rola para a última mensagem
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }
  
  // Enviar mensagem ao clicar no botão
  document.getElementById('send-button').addEventListener('click', function() {
    const userInput = document.getElementById('user-input').value;
  
    if (userInput.trim() !== '') {
      // Adiciona a mensagem do usuário
      addMessageToHistory(userInput, 'user');
      
      // Limpa o campo de input
      document.getElementById('user-input').value = '';
  
      // Simula uma resposta do bot
      setTimeout(function() {
        addMessageToHistory('Bot: ' + userInput, 'bot');
      }, 1000); // O bot responde após 1 segundo (simulação)
    }
  });
  
  // Também adiciona a funcionalidade para pressionar Enter para enviar a mensagem
  document.getElementById('user-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
      document.getElementById('send-button').click();
    }
  });