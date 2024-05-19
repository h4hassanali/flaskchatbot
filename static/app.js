// class Chatbox {
//     constructor() {
//         this.args = {
//             openButton: document.querySelector('.chatbox__button'),
//             chatBox: document.querySelector('.chatbox__support'),
//             sendButton: document.querySelector('.chatbox__send--footer'), // Changed to match the HTML
//             inputField: document.querySelector('.chatbox__footer input') // Added input field selector
//         }

//         this.state = false;
//         this.messages = [];
//     }

//     display() {
//         const { openButton, chatBox, sendButton, inputField } = this.args;

//         openButton.addEventListener('click', () => this.toggleState(chatBox))

//         sendButton.addEventListener('click', () => this.onSendButton(chatBox, inputField))

//         inputField.addEventListener("keyup", ({key}) => {
//             if (key === "Enter") {
//                 this.onSendButton(chatBox, inputField)
//             }
//         })
//     }

//     toggleState(chatbox) {
//         this.state = !this.state;

//         // Show or hide the box
//         if(this.state) {
//             chatbox.classList.add('chatbox--active')
//         } else {
//             chatbox.classList.remove('chatbox--active')
//         }
//     }

//     onSendButton(chatbox, inputField) {
//         var text1 = inputField.value.trim(); // Modified to trim whitespace
//         if (text1 === "") {
//             return;
//         }

//         let msg1 = { name: "User", message: text1 }
//         this.messages.push(msg1);

//         fetch('/get_response', { // Modified to match Flask route
//             method: 'POST',
//             body: JSON.stringify({ question: text1 }), // Modified to match Flask request format
//             headers: {
//               'Content-Type': 'application/json'
//             },
//           })
//           .then(response => response.json())
//           .then(data => {
//             let msg2 = { name: "Sam", message: data.response };
//             this.messages.push(msg2);
//             this.updateChatText(chatbox)
//             inputField.value = ''

//         }).catch((error) => {
//             console.error('Error:', error);
//             this.updateChatText(chatbox)
//             inputField.value = ''
//           });
//     }

//     updateChatText(chatbox) {
//         var html = '';
//         this.messages.slice().reverse().forEach(function(item, index) {
//             if (item.name === "Sam")
//             {
//                 html += '<div class="messages__item messages__item--operator">' + item.message + '</div>' // Changed class to match HTML
//             }
//             else
//             {
//                 html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>' // Changed class to match HTML
//             }
//           });

//         const chatmessage = chatbox.querySelector('.chatbox__messages');
//         chatmessage.innerHTML = html;
//     }
// }


// const chatbox = new Chatbox();
// chatbox.display();
class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.chatbox__send--footer'), // Changed to match the HTML
            inputField: document.querySelector('.chatbox__footer input') // Added input field selector
        }

        // Define the audio object and load the audio file
        this.audio = new Audio('/static/audio/tip_small.mp3');

        this.state = false;
        this.messages = [];
    }

    display() {
        const { openButton, chatBox, sendButton, inputField } = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox, inputField))

        inputField.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox, inputField)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // Show or hide the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox, inputField) {
        var text1 = inputField.value.trim(); // Modified to trim whitespace
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);

        fetch('/get_response', { // Modified to match Flask route
            method: 'POST',
            body: JSON.stringify({ question: text1 }), // Modified to match Flask request format
            headers: {
              'Content-Type': 'application/json'
            },
          })
          .then(response => response.json())
          .then(data => {
            let msg2 = { name: "Sam", message: data.response };
            this.messages.push(msg2);
            this.updateChatText(chatbox)
            inputField.value = ''

            // Play the message tone
            this.playMessageTone();

        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            inputField.value = ''
          });
    }

    playMessageTone() {
        this.audio.play();
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "Sam")
            {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>' // Changed class to match HTML
            }
            else
            {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>' // Changed class to match HTML
            }
          });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}


const chatbox = new Chatbox();
chatbox.display();
