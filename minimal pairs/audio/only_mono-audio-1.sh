#!/usr/bin/env bash

for i in {91..92}; do
  ffmpeg -i original-audio-1/recording_kannada_$i.aac -af "pan=mono|c0=c0" audio-1/kannada_minimal_1_$i.aac
done
