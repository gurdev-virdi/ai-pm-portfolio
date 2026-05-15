Feature: Image generation
Local approach:
Pro - Fast, can be as 150-300ms on A18 Pro
Pro -More private as data and requests and processed locally
​​Pro - Works anywhere without dependency on internet connection
Con - Limited model size (4-7B parameters max). This could impact result quality
Con - Battery usage impact to process images

Cloud approach: 
Pro - Unlimited model size (70B+). 
Pro - Better result quality from larger models
Pro - Saves battery
Con - Privacy since data is processed on the cloud and subject to the cloud providers usage and data governance policies
Con - Costs to use cloud compute / API calls


Your decision: Apple Intelligence’s philosophy is to service 80% of users requests locally, with 20% in the cloud. This might lead you to assume that users need a toggle, but that introduces additional complexity for the user. The best solution here from an experience standpoint would be to generate the first set of images locally, so that the user gets a quick response and can see a few options. We could show 4 by default, which should give the user enough options to choose from. If they want more, this is when we send the request to the cloud once they tap a button like “See more”, where we then route the user’s request to a larger model (7B+). 

 I would give users a toggle to choose which they would want for image generation, with the default set to generate locally. If users try that approach and get a fast response that they don’t like, they could always generate more options on the cloud. The challenge with image generation is that you usually want to see a few options before you decide. Users may be more willing to use the cloud to get a better quality result for non-sensitive requests. They should have that flexibility, but default users into using the local, fast, private option. 
