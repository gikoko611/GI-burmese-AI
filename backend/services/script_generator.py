from backend.schemas import (
    GenerateScriptRequest,
    GenerateScriptResponse,
    ScriptSegment,
)


def generate_script(request: GenerateScriptRequest) -> GenerateScriptResponse:
    video_id = "unknown"

    if request.analysis:
        video_id = request.analysis.videoId

    script = (
        "မင်္ဂလာပါ။ ဒီဗီဒီယိုကို Burmese AI နဲ့ ပြန်လည်တင်ပြပေးပါမယ်။\n\n"
        "လက်ရှိ Backend က Demo Mode ဖြစ်တဲ့အတွက် မူရင်းဗီဒီယိုရဲ့ "
        "transcript သို့မဟုတ် audio ကို မရရှိသေးပါ။ "
        "ဒါကြောင့် အောက်ပါစာသားဟာ real video recap မဟုတ်ဘဲ "
        "pipeline စမ်းသပ်ရန်အတွက် demo script ဖြစ်ပါတယ်။\n\n"
        f"Video ID: {video_id}\n"
        f"Content Type: {request.contentType}\n"
        f"Script Length: {request.scriptLength}\n"
        f"Narration Style: {request.narrationStyle}\n"
    )

    segments = [
        ScriptSegment(
            timestamp="00:00",
            heading="Introduction",
            content="ဒီအပိုင်းမှာ ဗီဒီယိုအကြောင်းအရာကို မိတ်ဆက်ပေးထားပါတယ်။",
        ),
        ScriptSegment(
            timestamp="00:30",
            heading="Main Content",
            content="Real transcript provider ချိတ်ဆက်ပြီးနောက် ဒီနေရာမှာ "
                    "ဗီဒီယိုထဲက အဓိကအချက်အလက်တွေကို Burmese လို "
                    "သဘာဝကျကျ ပြန်လည်ရေးသားပေးပါမယ်။",
        ),
        ScriptSegment(
            timestamp="01:00",
            heading="Conclusion",
            content="Transcript ရရှိလာတဲ့အခါ အဓိကအချက်တွေကို စုစည်းပြီး "
                    "နောက်ဆုံးအနှစ်ချုပ်ကို ထုတ်ပေးနိုင်ပါမယ်။",
        ),
    ]

    return GenerateScriptResponse(
        success=True,
        script=script,
        segments=segments,
        wordCount=len(script.split()),
        characterCount=len(script),
        estimatedDuration=request.scriptLength,
        isDemoMode=True,
        disclaimer=(
            "Demo Mode: no real transcript or video media was processed. "
            "Connect an authorized transcript provider for real video-based "
            "Burmese script generation."
        ),
    )
