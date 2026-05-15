Question (Week 1, Question 3):

"How would you decide which AI model to use for a new feature at Apple?"

This is a framework question. They want to see structured thinking, not a list of models.
Strong answer structure:
Start with the constraints that narrow the decision space, not the models themselves:

Privacy/data classification — Does this data leave the device? Apple defaults to on-device. If it does go to the cloud, PCC or 3rd party?
Latency requirement — User-facing interaction (< 200ms) vs. background processing (seconds acceptable)
Model capability floor — What's the minimum quality that doesn't embarrass Apple? (Apple's bar is higher than most)
Cost at scale — Token cost × DAU × calls/session. Build the unit economics before committing.
Fallback strategy — What happens when the model fails or the user is offline?

Then bring it to a real example: "For a keyboard autocomplete feature like what Apple Intelligence does, I'd start with a compressed on-device model (< 3B parameters to fit within iPhone memory constraints) because latency requirements are sub-100ms and keystrokes are highly sensitive. I'd only route to PCC for longer-form generation where quality matters more than instant response."
Common mistake: Jumping straight to "I'd evaluate GPT-4 vs Claude." That sounds like a developer, not a PM. Lead with constraints, not tools.
