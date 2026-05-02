# Report #1

Our current implementation contains high coupling and low cohesion such as `clips.py`. This makes it hard to test, swap components or scale any individual part without breaking the others.

I want to scale and improve our current implementation so the following approach will be used.

## New Implementation

The basic flow of would be in the following key steps:

**1.** User uploads a long form content

**2.** The input video gets put into a queue (Videos will be stored in Amazon Simple Storage Service S3 bucket)

**3.** Backend Process

**3.1** Downloads the long form video

**3.2** Creates the clips from long form video and saved in the same S3 bucket

**4** Frontend process

**4.1** Finds clips and presents them to user

Note: we will use a S3 key to uniquely identify and retrieve videos inside S3.
