# Banana Store
~~Browser~~ Mirror


> **Built for the Nano Banana Hackathon** - AI-powered e-commerce that shows customers how they look wearing products before purchase.

## What Makes Banana Different

**Proactive AI Personalization**: Unlike traditional virtual try-on apps that wait for user requests, Banana automatically generates personalized images as you browse - no manual try-on needed.

- **Traditional**: Static photos → Imagination → Uncertainty
- **Virtual Try-On**: Manual requests → Wait → Limited engagement  
- **Banana**: Automatic personalization → Instant visualization → Confident purchases

## Key Features

- **Proactive AI**: Automatic image generation using Google GenAI (Gemini 2.5 Flash)
- **Real-time Processing**: Background generation with progress indicators
- **User Profiles**: JWT authentication with profile image upload
- **Responsive Design**: Mobile-first, works on all devices
- **Modern UI**: Sliding home carousel with curated fashion imagery, hover effects, smooth transitions

## Quick Start

1. **Clone & Install**:
   ```bash
   git clone <repository-url>
   cd BananaShop
   uv sync
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Add your GOOGLE_API_KEY
   ```

3. **Run Application**:
   ```bash
   uv run uvicorn main:app --reload
   ```

4. **Access**: Open `http://localhost:8000`

## Expansion Potential

Banana's proactive personalization can extend beyond fashion:
- **Furniture**: Visualize items in your actual space
- **Automotive**: Customize vehicles in your environment  
- **Beauty**: Virtual makeup and styling
- **Electronics**: Device integration and sizing

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, JWT Authentication
- **AI**: Google Generative AI (Gemini 2.5 Flash Image Preview)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Database**: SQLite
- **Package Manager**: UV

## Assumptions & Disclaimers

- Generated images cached client-side for performance
- Requires JavaScript and modern browser support
- Product images and home carousel visuals sourced from Zara.com for demonstration
- Educational project - not for commercial use without proper licensing

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

Built with ❤️ for the future of AI-powered shopping experiences.
