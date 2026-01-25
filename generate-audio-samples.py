from pathlib import Path

from gtts import gTTS

audio_samples = {
    "sample-recording-1-task-with-due-date-and-reminder.mp3": "Follow up with my boss, latest by August 30th, remind me August 20th. We should talk about our AI strategy!",
    "sample-recording-2-random-thoughts.mp3": "These are just some random thoughts. I need to think about that some time soon-ish",
    "sample-recording-3-send-email.mp3": "send an email to myself to remind me to find out what 42 is about",
}

output_dir = Path(__file__).resolve().parent / "audio_samples"
output_dir.mkdir(parents=True, exist_ok=True)

for filename, text in audio_samples.items():
    tts = gTTS(text, lang="en")
    destination = output_dir / filename
    tts.save(str(destination))
