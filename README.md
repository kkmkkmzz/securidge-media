# securidge-media

Securidge YouTube 영상 보관소 및 제작 도구.

- `RUNBOOK.md` : 매일 05:00(쇼츠)·16:00(롱폼) 제작 절차와 편집·출처 원칙
- `videos/<날짜>-<슬롯>-<주제>/` : video.mp4, script.txt, spec.json, sources.md, meta.json, narration.mp3, words.json
- `videos/styles_used.json` : 영상별 그림체 기록 (같은 조합 재사용 금지)
- `tools/securidge_render.py` : 렌더러 (1.5초 정지 오프닝, 쇼츠 1080x1920 / 롱폼 1920x1080, 그림체 14종 순환)
- `tools/fonts/` : SIL OFL 폰트 (OFL.txt)
- `research/approved.md` : 영상에 소개해도 되는 KM 논문 목록
