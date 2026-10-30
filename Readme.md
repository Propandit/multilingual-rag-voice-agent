# Story of Change — AI Comic Studio

### Turn a visitor's real experience into a comic starring them.

**Story of Change** is a MERN application developed for a **Google Cloud event experience**. Visitors take a photo, choose a business field, and share a short story. The application turns that input into a complete, personalized **six-panel graphic novel** with English dialogue and captions.

The result is a digital takeaway: visitors can read their comic, download it from a mobile QR page, print it, and explicitly approve it for the event's four display screens.

![Story of Change pipeline: visitor input, validated story planning, reference-guided artwork, face-aware lettering, storage and event delivery](github-comic-gen-assets/comic-generation-pipeline.png)

[Open the editable SVG diagram](github-comic-gen-assets/comic-generation-pipeline.svg)

## What visitors can do

- Start without creating an account.
- Capture their character reference with a camera and a visible **3-second countdown**.
- Choose a field: finance, retail, healthcare, manufacturing, technology, or business services.
- Type a story of **at least 20 words**, or record up to **60 seconds** of voice input.
- Become the main character in six connected illustrated scenes.
- Read the complete page or explore it panel by panel.
- Scan a QR code to open a mobile page with **only the comic and a Download button**.
- Print the complete comic on one A4 sheet.
- Approve their comic for the visitor displays.

New comics use one approved **Agents of Change** graphic-novel style. The backend selects one of six page layouts automatically; visitors do not need to choose an art style or arrange panels.

## The visitor journey

| Step | What happens |
| --- | --- |
| 1. Your portrait | Open the camera, take a photo after the countdown, and optionally enter a character name. |
| 2. Your world | Choose the business field that fits the story. |
| 3. Your story | Describe the challenge, the change, and the outcome in at least 20 words. Voice transcripts remain editable. |
| 4. Generation | The backend plans and validates the story, creates six images, and composes the finished page. |
| 5. The reveal | Read the comic, inspect individual panels, scan the QR, or print. |
| 6. Your approval | Select **Add my story to the wall** to make it eligible for the event displays. |
| 7. The next visitor | The success screen returns to the start after 60 seconds. |

## How the generation pipeline works

### 1. Collect the visitor's input

The React kiosk gathers a camera photo, a selected field, an optional name, and the story. Stories must contain at least 20 words and stay within 4,000 characters; line breaks are optional.

Voice input uses **Google Cloud Speech-to-Text**. Audio is converted to mono PCM WAV and validated before transcription. The recognized words remain editable, while the generated comic's dialogue and captions are in English.

### 2. Plan and validate the complete story

The Express backend checks storage availability before beginning paid generation. It selects a page layout and sends the story, field, instructions, and reference photo to the configured text model through **Replicate**.

The model must return:

- An expanded story and a shared character description.
- Exactly six numbered panel descriptions.
- An image-generation prompt for every panel.
- English dialogue and captions.
- Character references, scene composition, and proposed lettering regions.

The backend validates this plan and checks whether the approved words fit before requesting artwork. Panel six must resolve the story.

### 3. Generate the artwork with shared references

**Panel 1 is generated first. Panels 2–6 then run concurrently.** The output stays in numbered reading order.

Each image request includes the original camera photo. Panels 2–6 also use panel 1 as a visual reference. A shared character description and the approved style reference guide appearance, clothing, ink, and color treatment across the story.

If a panel fails, successful panels are retained. Retry resumes known work or unfinished panels instead of regenerating the whole comic automatically.

### 4. Place lettering around the finished artwork

After artwork is saved, the backend locates visible heads in the generated images. The compositor maps those positions into the page layout and places speech balloons, narration, and tails around protected regions.

The same SVG compositor drives the preview, reader, and exports. It measures the bundled fonts, preserves complete approved text, and keeps the full artwork visible. Invalid lettering blocks download and publication until it is resolved.

Face localization is model-based and can miss details. It improves placement but does not guarantee perfect visual results. Visitors and operators should inspect the page; an optional model review supplies additional feedback without automatically redrawing the comic.

### 5. Save the finished comic

**MongoDB** stores comic metadata, generated panel artwork, review state, and the approved display queue. Artwork is stored separately from the metadata.

**Google Cloud Storage** stores the fully composed **1600 × 3200 PNG** in a private bucket. Object names combine a UTC timestamp, a safe character-name slug, the comic ID, and a page-version suffix. The original camera portrait is not uploaded to this bucket.

A cloud-saving failure retains the completed images so the operator can retry saving without paying to draw them again.

### 6. Deliver the visitor's takeaway

The QR contains a short public page address:

```text
https://YOUR_FRONTEND_DOMAIN/download/COMIC_ID
```

That page displays the complete saved comic and a **Download comic** button. When the button is tapped, the application requests a current signed GCS link and downloads the PNG. The bucket remains private; signed links provide temporary access. See Google's [signed URL documentation](https://docs.cloud.google.com/storage/docs/access-control/signed-urls).

The QR page address is separate from the expiring GCS URL, so a refreshed download does not need a newly generated comic.

### 7. Show approved stories on the event displays

A comic enters the display rotation only after explicit approval. The four display pages share the backend's queue and show distinct approved comics when enough stories are available.

The display clients poll the API every **2 seconds**. The backend schedules **30-second** rotations. This implementation uses HTTP polling, not WebSockets.

## Technology stack

| Layer | Technology and purpose |
| --- | --- |
| Frontend | React, Vite, React Router, and CSS for the kiosk, reader, mobile download page, and displays. |
| Backend | Node.js and Express for validation, generation jobs, storage, exports, and display scheduling. |
| Database | MongoDB for saved comics, generated artwork, and shared event state. |
| Story planning | `google/gemini-3-flash` through Replicate, configurable on the backend. |
| Image generation | `google/nano-banana-2` through Replicate, using the visitor photo and reference artwork. |
| Voice input | Google Cloud Speech-to-Text using a separate backend API key. |
| Final-page storage | Private Google Cloud Storage with signed download links. |
| Composition | SVG layout and lettering, rasterized PNG export, and PDF export support. |
| QR generation | Generated locally by the backend; no third-party QR service is needed. |

**Model requests use Replicate. A direct `GEMINI_API_KEY` is not used by this application.** Replicate usage and Google Cloud usage are billed separately.

## Repository structure

```text
comic-wall/
├── backend/
│   ├── app.js                 # API routes and generation orchestration
│   ├── server.js              # API entry point
│   ├── build.js               # Bundled production backend build
│   ├── replicate.js           # Model requests, polling and retries
│   ├── prompts.js             # Story and image instructions
│   ├── faceLocations.js       # Head localization in generated artwork
│   ├── composition.js         # Preview and export rendering
│   ├── repository.js          # MongoDB persistence and display state
│   ├── gcs.js                 # Private cloud storage and signing
│   ├── delivery.js            # Mobile page links and QR generation
│   ├── scripts/               # GCS checks and synchronization
│   └── test/
├── frontend/
│   ├── src/pages/             # Studio, reader, mobile download and displays
│   ├── src/components/        # Camera, voice, comic preview and delivery UI
│   ├── src/lib/               # Reusable JavaScript rules and style registry
│   ├── src/services/          # API access and browser services
│   ├── src/styles/            # Event kiosk and responsive mobile styling
│   └── public/assets/         # Bundled fonts and visual assets
├── start.bat                  # Windows development launcher
└── README.md
```

There is no root npm package. Install and run the frontend and backend separately. Backend source imports some reusable rules from `frontend/src/lib/`, so keep both source directories together when developing or building.

## Install and run locally

### Requirements

- Node.js **22.13 or newer**, npm, and Git.
- A reachable MongoDB instance.
- A Replicate account with a valid token, model access, and available billing/credits.
- A Google Cloud project and a private Cloud Storage bucket.
- A camera-equipped computer or kiosk.
- A microphone and Speech-to-Text configuration if voice input is enabled.

### 1. Get the code and dependencies

```bash
git clone https://github.com/tagglabs/google26-aoc.git
cd google26-aoc/comic-wall
npm --prefix backend ci
npm --prefix frontend ci
```

Stop running development servers before reinstalling dependencies on Windows if native-module files are locked.

### 2. Configure the backend

Copy `backend/.env.example` to `backend/.env`. Use your own credentials and infrastructure values:

```dotenv
HOST=127.0.0.1
PORT=5000
GOOGLE26_COMIC_WALL_MONGO_URI=mongodb://127.0.0.1:27017/story_of_change

REPLICATE_API_TOKEN=YOUR_REPLICATE_TOKEN
REPLICATE_TEXT_MODEL=google/gemini-3-flash
REPLICATE_IMAGE_MODEL=google/nano-banana-2

GOOGLE_SPEECH_API_KEY=YOUR_OPTIONAL_SPEECH_KEY
GOOGLE_SPEECH_LANGUAGE=en-IN

GOOGLE_CLOUD_PROJECT=YOUR_GOOGLE_CLOUD_PROJECT
GCS_BUCKET=YOUR_PRIVATE_COMIC_BUCKET
GCS_PREFIX=final-comics
GCS_DOWNLOAD_TTL_SECONDS=86400
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json

PUBLIC_COMIC_BASE_URL=https://YOUR_FRONTEND_DOMAIN
ALLOW_HTTP_COMIC_BASE_URL=false
```

| Setting | Where it comes from |
| --- | --- |
| `GOOGLE26_COMIC_WALL_MONGO_URI` | Your MongoDB connection string, including the database name. This is the only MongoDB environment setting. |
| `REPLICATE_API_TOKEN` | Your Replicate account. Used for planning, image generation, face localization, and visual review. |
| `GOOGLE_SPEECH_API_KEY` | Your Google Cloud project with Speech-to-Text enabled. Optional when visitors type their stories. |
| `GOOGLE_APPLICATION_CREDENTIALS` | The absolute path to backend-only service-account credentials, or use a supported ADC setup with signing capability. |
| `PUBLIC_COMIC_BASE_URL` | The public **frontend** address that hosts the mobile download page, not the API address. |

Enable billing and the Speech-to-Text API if using voice input. Google's [Speech-to-Text setup guide](https://docs.cloud.google.com/speech-to-text/docs/setup?hl=en) covers project preparation.

Keep the GCS bucket private with uniform bucket access and public access prevention. The backend identity needs the object access required to save, read, list, and delete the application's pages, plus the ability to sign downloads. A Speech-to-Text API key does not authenticate Cloud Storage. See Google's [V4 signing guide](https://docs.cloud.google.com/storage/docs/access-control/signing-urls-with-helpers) for signing identities and permissions.

Never commit `.env` files or service-account JSON. All provider credentials belong on the backend; `VITE_` settings are public browser configuration.

### 3. Start the application

Use separate terminals from the `comic-wall` directory:

```bash
# Terminal 1
npm --prefix backend start
```

```bash
# Terminal 2
npm --prefix frontend start
```

Open **http://localhost:3000**. The API runs on **http://127.0.0.1:5000**. On Windows, `start.bat` can start the two applications after configuration.

### 4. Verify storage

```bash
npm --prefix backend run gcs:check
```

This checks cloud access and download signing without starting image generation. Generation also requires MongoDB to be available.

### 5. Test the mobile QR on the same Wi-Fi

Use the computer's actual Wi-Fi IPv4 address, not `localhost` or `0.0.0.0`:

```dotenv
# backend/.env — local testing only
PUBLIC_COMIC_BASE_URL=http://YOUR_PC_WIFI_IP:3000
ALLOW_HTTP_COMIC_BASE_URL=true
```

```dotenv
# frontend/.env.local — local testing only
VITE_DEV_HOST=0.0.0.0
VITE_API_URL=/api
```

Restart both applications and refresh the comic page before scanning the new QR. The phone and computer must be on the same network, with access to port 3000. Use localhost for camera capture on the computer; the phone reader does not need a camera.

Local Wi-Fi QR codes are not globally reachable. Production rejects HTTP reader addresses when `NODE_ENV=production`.

## Set up the Google Cloud event experience

### Equipment and screen roles

| Role | Setup |
| --- | --- |
| Visitor kiosk | A camera-equipped computer, portrait touchscreen or monitor, and a browser. A microphone is optional. |
| Operator | A computer for monitoring provider availability, failed jobs, and the display queue. |
| Visitor displays | Up to four browser-connected screens, each opening its assigned display route. |
| Visitor takeaway | The visitor's phone opens the QR page; an optional printer provides a paper copy. |
| Infrastructure | An HTTPS frontend, one running API process, MongoDB, Replicate access, and private GCS storage. |

The kiosk design uses a **1080 × 1920 portrait artboard** that scales to the browser. The finished comic is independently composed at **1600 × 3200**.

### Event-day sequence

1. Start the API and frontend, confirm MongoDB connectivity, and run `gcs:check`.
2. Open `/` on the kiosk. Check camera permission, framing, lighting, and the microphone if enabled.
3. Open `/display/1`, `/display/2`, `/display/3`, and `/display/4` on the audience screens. Use `/wall` for the combined overview.
4. Create a test story, inspect all six panels and lettering, and verify the mobile download using a phone.
5. Check the print preview fits one A4 page, then test the connected printer.
6. Approve the test comic and confirm it enters the display rotation.
7. Keep the API running during generation. Monitor credits, network availability, and visitor waiting time during the event.

No story is published to the audience displays merely because generation finished. Approval remains a separate visitor action.

### Public hosting and globally accessible QR codes

Build **both** applications from the full source checkout:

```bash
npm --prefix frontend run build
npm --prefix backend run build
```

| Output | How it is used |
| --- | --- |
| `frontend/dist/` | Serve as static files through an HTTPS web server or frontend host. |
| `backend/dist/index.js` and `backend/dist/assets/` | Run the bundled API with Node.js and the backend production npm dependencies. |

The backend build bundles the shared JavaScript rules and copies the style reference and fonts. Keep its runtime assets with the bundle. For a bundled deployment that retains the `backend/` directory, install runtime dependencies with `npm --prefix backend ci --omit=dev` **after** building, then run:

```bash
node backend/dist/index.js
```

For same-origin hosting, route `/api` to Express and serve the frontend from the same HTTPS domain. For separate hosts, set this public frontend variable **before building**:

```dotenv
# frontend/.env.production
VITE_API_URL=https://YOUR_API_DOMAIN/api
```

Set production backend values:

```dotenv
NODE_ENV=production
PUBLIC_COMIC_BASE_URL=https://YOUR_FRONTEND_DOMAIN
ALLOW_HTTP_COMIC_BASE_URL=false
CORS_ORIGINS=https://YOUR_FRONTEND_DOMAIN
```

Include any API path prefix in `VITE_API_URL` if your host uses one. Configure the frontend host to send routes such as `/download/COMIC_ID` to `index.html`; Nginx can use `try_files $uri $uri/ /index.html`.

The public mobile page, its assets, and the delivery API must be reachable from a visitor's phone. The API must still be able to read MongoDB and access GCS. Once these are deployed, newly displayed production QR codes can work across networks; they are not limited to the event Wi-Fi.

Run **one API process** for the current architecture: active jobs live in memory. Use a process manager or service to keep it running, and wait for generation to finish before restarting. Do not assume this implementation supports stateless autoscaling or multiple independent job workers.

Because there is no visitor login and generation can incur charges, protect generation and mutation endpoints with event-appropriate access controls and quotas. The public reader does not need to expose the creation flow to everyone.

## Use cases

| Setting | How the comic experience can be used |
| --- | --- |
| Google Cloud events and technology conferences | Turn a visitor's cloud or AI transformation story into a personal takeaway and an approved audience display. |
| Enterprise innovation showcases | Illustrate how a team solved a workflow problem or changed a customer experience. |
| Trade shows and brand activations | Give visitors a participatory booth experience with a mobile souvenir. |
| Employee recognition | Celebrate a team member's improvement, contribution, or milestone. |
| Learning and training workshops | Turn a participant's scenario into a visual story for discussion. |
| Museums and visitor centers | Let visitors create a story connected to an exhibition or learning theme. |
| Customer-success events | Help customers explain their challenge, approach, and outcome in a visual format. |

These are example applications of the existing photo-to-comic flow, not claims of separate integrations or built-in training systems.

## Storage, privacy, and operational behavior

- The original camera photo is held in memory for the active/retryable job and released after completion or expiry. It is not stored in MongoDB, GCS, or the local server filesystem by this application.
- The photo is sent to Replicate to guide the character illustration. Provider-side processing and retention are separate from application storage.
- Finished comics contain the visitor's illustrated likeness. Explain this experience and the optional display publication to visitors during event onboarding.
- MongoDB preserves saved comics and display state across API restarts. In-memory unfinished jobs do not survive a restart.
- The GCS bucket stays private. A signed download link can be used by anyone who possesses it until it expires; there is no account-based authorization on the mobile reader.
- Completed panels and known prediction states are reused when possible. A failed placement or cloud-saving step does not automatically redraw all images.
- Generation time and cost vary with model latency, retries, reviews, and workload. There is no guaranteed completion time in this README.

## Output formats

| Output | Details |
| --- | --- |
| PNG | Full comic at **1600 × 3200**, used for cloud storage and mobile downloads. |
| SVG | Embedded artwork with vector lettering and borders, used by the compositor and print preparation. |
| Native print | Complete comic fitted to one **A4 portrait** sheet without opening a new application page. |
| API PDF export | Raster comic on a **4 × 8 ft** media box; the large physical page does not add image resolution. |

## Useful commands

```bash
# Tests
npm --prefix backend test
npm --prefix frontend test
npm --prefix backend run test:db

# Production artifacts
npm --prefix frontend run build
npm --prefix backend run build

# Preview the built frontend on port 4173; start the API separately
npm --prefix frontend run preview

# Check GCS access and signing
npm --prefix backend run gcs:check

# Save existing ready pages to GCS without regenerating their artwork
npm --prefix backend run gcs:sync
```

Use a development/test MongoDB service for `test:db`; it creates and drops isolated temporary databases. Tests do not replace an event rehearsal with the real camera, microphone, phone, and printer.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `npm run build` fails at the repository root | Run the per-application build commands above; there is no root package. |
| A Windows install reports `EPERM` for a native module | Finish active jobs, stop the frontend/API processes, then retry dependency installation. |
| Camera cannot open | Use localhost or HTTPS, allow browser camera access, and close other apps using the camera. |
| The story cannot continue | Enter at least 20 words; punctuation alone does not count. |
| Generation is unavailable | Check the single MongoDB URI, Replicate token/model access, provider billing, and GCS readiness. |
| Voice transcription fails | Check the separate Speech-to-Text key, enabled API, billing, and microphone permission. |
| A QR downloads immediately instead of opening the mobile page | Deploy/restart the updated backend and frontend, then refresh the kiosk. An old QR still contains its old destination. |
| A QR works only on event Wi-Fi | Replace the local IP base URL with the public HTTPS frontend URL and refresh the displayed QR. |
| The mobile route shows a blank page or 404 | Check the frontend SPA fallback, `VITE_API_URL`, CORS configuration, and the delivery API response. |
| A comic is absent from the displays | Confirm it was explicitly approved and that all screens use the same API. |
| Download or print is blocked | Check lettering/face-placement status and cloud-saving errors; retry the failed stage. |

## Credits

The application combines React, Vite, Express, MongoDB, Replicate-hosted Google models, Google Cloud Speech-to-Text, and Google Cloud Storage. Lettering uses bundled **Comic Neue Bold Italic** and **Black Han Sans** fonts.

Google Cloud and provider names identify the services and event context used by the project. This README does not imply that all application components are Google products or that Google endorses a third-party deployment. Follow the repository's actual license and bundled asset licenses when reusing the code, fonts, or event branding.
