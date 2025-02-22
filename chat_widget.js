        const message = messageQueue.shift();
        displayChatMessage(message);
    }
}, 100);

const addMessageToQueue = (message) => {
    if (!message) return;
    messageQueue.push(message);
    processQueue();
};

/* ============= EVENT LISTENERS ============= */

window.addEventListener('onWidgetLoad', async (obj) => {
    try {
        duration = parseFloat("{{duration}}") || 5000;
        const status = await SE_API.getOverlayStatus();

        if (status?.isEditorMode) {
            setInterval(simulateMessageEvent, 2000);
            setTimeout(() => setInterval(simulateFollowerEvent, 5000), 1000);
        }
    } catch (error) {
        console.error('Widget load error:', error);
    }
});

window.addEventListener('onEventReceived', (obj) => {
    try {
        const { listener, event } = obj.detail;

        if (listener === "event:test") {
            simulateMessageEvent();
            setTimeout(simulateFollowerEvent, 1000);
            return;
        }

        if (listener === 'message' && event?.data?.text) {
            addMessageToQueue({
                username: event.data.displayName,
                text: event.data.text,
                badges: event.data.badges || [],
                emotes: event.data.emotes || []
            });
        } else if (event && EVENT_TYPES[listener]) {
            displayEventMessage(event, listener);
        }
    } catch (error) {
        console.error('Event handling error:', error);
    }
});

/* ============= SIMULATION FUNCTIONS ============= */

function simulateMessageEvent() {
    const event = new CustomEvent("onEventReceived", {
        detail: {
            listener: "message",
            event: {
                data: {
                    badges: [{
                        type: "broadcaster",
                        version: "1",
                        url: "https://static-cdn.jtvnw.net/badges/v1/5527c58c-fb7d-422d-b71b-f309dcb85cc1/3",
                        description: "Broadcaster"
                    }],
                    displayName: "TestUser",
                    text: "Hello World! 👋 NotLikeThis",
                    emotes: [{
                        type: "twitch",
                        name: "NotLikeThis",
                        id: "58765",
                        urls: {
                            "1": "https://static-cdn.jtvnw.net/emoticons/v2/58765/static/dark/1.0"
                        },
                        start: 19,
                        end: 30
                    }]
                }
            }
        }
    });
    window.dispatchEvent(event);
}

function simulateFollowerEvent() {
    const event = new CustomEvent("onEventReceived", {
        detail: {
            listener: "follower-latest",
            event: {
                avatar: "https://cdn.streamelements.com/assets/dashboard/my-overlays/overlay-default-preview-2.jpg",
                displayName: "NewFollower",
                providerId: "12345",
                name: "newfollower",
                type: "follower"
            }
        }
    });
    window.dispatchEvent(event);
}