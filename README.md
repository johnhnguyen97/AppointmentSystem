# Twitch Chat Overlay Widget

A JavaScript widget that handles Twitch chat messages and events with smooth animations.

## Features

- Real-time chat message display with badges and emotes
- Event handling (followers, subscribers, cheers, tips, raids)
- Smooth animations using GSAP
- Message queueing system
- Error handling and logging 
- Test mode simulation

## Dependencies

- [GSAP](https://greensock.com/gsap/) for animations
- [Lodash](https://lodash.com/) for debouncing
- StreamElements API for widget integration

## Installation

1. Create a new overlay in your StreamElements dashboard
2. Add a Custom Widget
3. Copy the contents of `chat_widget.js` into the JavaScript section
4. Configure the widget settings as needed

## Configuration

The widget accepts the following settings:

- `duration`: Display duration for messages in milliseconds (default: 5000)

## Usage

The widget automatically handles:

- Chat messages with badges and emotes
- Follower events
- Subscriber events
- Cheer events
- Tip events
- Raid events

## Development

### Project Structure

```
chat_widget.js        # Main widget implementation
```

### Code Organization

- **Initialization**: Basic setup and error checking
- **Configurations**: Animation and event type definitions
- **Utility Functions**: Helper functions like emote replacement
- **Animation Functions**: GSAP animation implementations
- **Message Handling**: Core message display logic
- **Event Listeners**: StreamElements event handling
- **Simulation Functions**: Test mode functionality

### TODO

- [ ] Add customizable themes
- [ ] Implement message filters
- [ ] Add sound effects support
- [ ] Create custom animation presets
- [ ] Add message moderation features

## Testing

The widget includes built-in simulation functions for testing:
- `simulateMessageEvent()`: Simulates a chat message
- `simulateFollowerEvent()`: Simulates a new follower

Test mode is automatically enabled in the StreamElements editor.

## Error Handling

The widget implements comprehensive error handling:
- DOM element validation
- GSAP dependency checking
- Try-catch blocks for critical operations
- Fallback animations
- Console error logging

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request
