import { ContentType, NarrationStyle, ScriptLength, OutputLanguage, GeneratedResult } from '../types';

interface MockScriptTemplate {
  title: string;
  burmeseSections: {
    sectionTitle: string;
    narration: string;
    notes?: string;
    timecode?: string;
  }[];
  englishSections: {
    sectionTitle: string;
    narration: string;
    notes?: string;
    timecode?: string;
  }[];
}

export const mockTemplates: Record<ContentType, MockScriptTemplate> = {
  'Technology': {
    title: 'AI နည်းပညာ တိုးတက်ပြောင်းလဲမှုများနှင့် အနာဂတ်အလားအလာ (AI Tech Revolution)',
    burmeseSections: [
      {
        sectionTitle: 'နိဒါန်း (Intro & Hook)',
        timecode: '00:00 - 00:45',
        narration: 'မင်္ဂလာပါ ခင်ဗျာ။ ဒီကနေ့ ဗီဒီယိုမှာတော့ ကမ္ဘာတစ်ဝန်း နည်းပညာလောကကို တစ်ဆစ်ချိုး ပြောင်းလဲပစ်နေတဲ့ မျိုးဆက်သစ် AI စနစ်တွေအကြောင်း စိတ်ဝင်စားဖွယ် ရှင်းပြပေးသွားမှာ ဖြစ်ပါတယ်။ မကြာသေးမီက ထွက်ပေါ်လာတဲ့ စွမ်းဆောင်ရည်မြင့် မော်ဒယ်တွေဟာ လူသားတွေရဲ့ နေ့စဉ်လုပ်ငန်းဆောင်တာတွေကို ဘယ်လို လျင်မြန်လွယ်ကူစေသလဲဆိုတာ အတူတူ လေ့လာကြည့်ကြရအောင်။',
        notes: 'အသံအနေအထားကို စိတ်လှုပ်ရှားဖွယ် နားထောင်ကောင်းအောင် အာရုံစိုက်ဖတ်ရှုရန်။'
      },
      {
        sectionTitle: 'အဓိက အချက်များ (Key Breakthroughs)',
        timecode: '00:45 - 03:00',
        narration: 'ပထမဆုံးအနေနဲ့ Multimodal Architecture ကို ကြည့်ရအောင်။ အရင်တုန်းက စာသားသက်သက်ပဲ နားလည်ခဲ့တဲ့ မော်ဒယ်တွေဟာ အခုဆိုရင် ဓာတ်ပုံ၊ အသံနဲ့ ဗီဒီယိုတွေကိုပါ တစ်ပြိုင်နက်တည်း ခွဲခြမ်းစိတ်ဖြာနိုင်လာပါပြီ။ ဥပမာအားဖြင့် ရှုပ်ထွေးတဲ့ ကုဒ်အမှားတွေကို စက္ကန့်ပိုင်းအတွင်း ရှာဖွေပြင်ဆင်ပေးနိုင်ပြီး လုပ်ငန်းခွင် စွမ်းဆောင်ရည်ကို ၃ ဆအထိ တိုးတက်စေပါတယ်။',
        notes: 'ဒုတိယပိုင်း နည်းပညာ အသုံးအနှုန်းများကို ရှင်းလင်းစွာ အသံထွက်ပါ။'
      },
      {
        sectionTitle: 'လက်တွေ့ အသုံးချမှုနှင့် အကျိုးကျေးဇူး (Real-World Applications)',
        timecode: '03:00 - 04:15',
        narration: 'ဒါ့အပြင် ဆေးဘက်ဆိုင်ရာ သုတေသနတွေ၊ ပညာရေးနဲ့ စီးပွားရေး လုပ်ငန်းတွေမှာ ဒီနည်းပညာကို ထိရောက်စွာ အသုံးပြုနေကြပါတယ်။ ကိုယ်ပိုင် လုပ်ငန်းတစ်ခုချင်းစီအတွက် အချိန်ကုန် သက်သာစေမယ့် အလိုအလျောက် စနစ်တွေကို တည်ဆောက်နိုင်ပြီ ဖြစ်ပါတယ်။',
        notes: 'စိတ်ဝင်စားမှု မြင့်မားစေရန် နမူနာများကို ထင်ရှားစွာ တင်ပြပါ။'
      },
      {
        sectionTitle: 'နိဂုံးနှင့် မေးခွန်း (Outro & Discussion)',
        timecode: '04:15 - 05:00',
        narration: 'သင်ရော ဒီလို နည်းပညာ တိုးတက်မှုအပေါ် ဘယ်လို ထင်မြင်ယူဆပါသလဲ? အနာဂတ်မှာ သင့်အလုပ်အကိုင်ကို ဘယ်လို အထောက်အကူပြုနိုင်မယ် ထင်ပါသလဲ? မှတ်ချက်ပေးခဲ့ကြပါဦး။ အခုလို အသိပညာမျှဝေမှု အစီအစဉ်တွေကို နှစ်သက်တယ်ဆိုရင် Like နဲ့ Subscribe လုပ်ထားဖို့ မမေ့ပါနဲ့ခင်ဗျာ။',
        notes: 'နိဂုံးချုပ် ဖိတ်ခေါ်စကားကို ယဉ်ကျေးပျူငှာစွာ ပြောကြားပါ။'
      }
    ],
    englishSections: [
      {
        sectionTitle: 'Introduction & Hook',
        timecode: '00:00 - 00:45',
        narration: 'Welcome everyone! Today we are exploring the game-changing advancements in next-generation AI architectures that are redefining industries across the globe.',
        notes: 'Keep energy high and engaging.'
      },
      {
        sectionTitle: 'Key Technological Breakthroughs',
        timecode: '00:45 - 03:00',
        narration: 'First, let us look at native multimodal models. Instead of single-modality processing, these architectures understand text, high-res images, and audio seamlessly in real time.',
        notes: 'Highlight speed and reasoning metrics.'
      },
      {
        sectionTitle: 'Practical Real-World Impact',
        timecode: '03:00 - 04:15',
        narration: 'From automated coding assistance to medical diagnostics and personalized learning tutors, productivity gains are scaling at an unprecedented rate.',
        notes: 'Pace evenly.'
      },
      {
        sectionTitle: 'Conclusion & Call to Action',
        timecode: '04:15 - 05:00',
        narration: 'What are your thoughts on these innovations? Share in the comments below, and do not forget to subscribe for more deep dives!',
        notes: 'Warm closing delivery.'
      }
    ]
  },
  'Movie Recap': {
    title: 'ဇာတ်ကားပြန်လည်သုံးသပ်ချက်နှင့် အကျဉ်းချုပ် (Cinema Narrative Recap)',
    burmeseSections: [
      {
        sectionTitle: 'အဖွင့်ဇာတ်လမ်း (Opening Hook)',
        timecode: '00:00 - 00:50',
        narration: 'ဒီဇာတ်ကားကတော့ အထီးကျန်ဆန်တဲ့ မြို့တော်ကြီးတစ်ခုမှာ လျှို့ဝှက်ဆန်းကြယ်စွာ ဖြစ်ပွားခဲ့တဲ့ ဖြစ်ရပ်တစ်ခုနဲ့ စတင်ထားပါတယ်။ ဇာတ်ကောင်ဟာ သာမန်ဘဝကနေ မမျှော်လင့်ဘဲ မာဖီးယားဂိုဏ်းကြီးရဲ့ ပစ်မှတ် ဖြစ်လာတဲ့အခါ...',
        notes: 'သည်းထိတ်ရင်ဖို ပုံစံဖြင့် ဇာတ်လမ်းဆွဲဆောင်မှုကို ဖန်တီးပါ။'
      },
      {
        sectionTitle: 'ဇာတ်လမ်း အလှည့်အပြောင်း (Rising Action & Twist)',
        timecode: '00:50 - 03:20',
        narration: 'ရဲတပ်ဖွဲ့ရဲ့ လိုက်လံဖမ်းဆီးမှုနဲ့အတူ သူရှာဖွေတွေ့ရှိလိုက်တဲ့ လျှို့ဝှက်ကုဒ်စာရွက်က တစ်မြို့လုံးရဲ့ အနာဂတ်ကို ပြောင်းလဲပစ်နိုင်စွမ်း ရှိနေပါတယ်။ သူယုံကြည်ခဲ့ရတဲ့ သူငယ်ချင်းအရင်းကတောင် သစ္စာဖောက်မှုမှာ ပါဝင်နေတာကို သိလိုက်ရတဲ့ အချိန်မှာတော့ ပွဲက ပိုမို ပြင်းထန်လာခဲ့ပါတယ်။',
        notes: 'အရှိန်အဟုန်ပြင်းစွာ ဇာတ်ကွက်ဆွဲတင်ပါ။'
      },
      {
        sectionTitle: 'အဆုံးသတ် ရလဒ် (Climax & Resolution)',
        timecode: '03:20 - 05:00',
        narration: 'နောက်ဆုံး မိနစ်မှာတော့ မဖြစ်နိုင်ဘူးလို့ ထင်ရတဲ့ ထွက်ပေါက်တစ်ခုကို ဖန်တီးပြီး တရားမျှတမှုကို သူကိုယ်တိုင် ပြန်လည်ရယူနိုင်ခဲ့ပါတယ်။ ဇာတ်သိမ်းပိုင်းမှာ ပရိသတ် မထင်မှတ်ထားတဲ့ ဒုတိယလှည့်ကွက်တစ်ခု ပါဝင်နေပြီး ကြည့်ရှုသူတိုင်းကို ရင်သပ်ရှုမောစေခဲ့ပါတယ်။',
        notes: 'စိတ်ကျေနပ်ဖွယ် နိဂုံးအသံဖြင့် ဖတ်ရှုရန်။'
      }
    ],
    englishSections: [
      {
        sectionTitle: 'Opening Scene',
        timecode: '00:00 - 00:50',
        narration: 'The story kicks off in a gritty neo-noir metropolis where an innocent bystander stumbles across an encrypted ledger that powerful cartels will kill to protect.',
        notes: 'Dramatic pacing.'
      },
      {
        sectionTitle: 'The Plot Twist',
        timecode: '00:50 - 03:20',
        narration: 'When his closest confidant betrays him at the central terminal, our protagonist realizes nobody can be trusted in this high-stakes game of survival.',
        notes: 'Build intensity and suspense.'
      },
      {
        sectionTitle: 'Climax & Final Revelation',
        timecode: '03:20 - 05:00',
        narration: 'In a stunning rooftop confrontation, the truth comes out with a shockwave twist that changes everything you thought you understood from the beginning.',
        notes: 'Resonant and satisfying tone.'
      }
    ]
  },
  'Tutorial / How-to': {
    title: 'အဆင့်ဆင့် လက်တွေ့လမ်းညွှန်သင်ခန်းစာ (Step-by-Step Practical Guide)',
    burmeseSections: [
      {
        sectionTitle: 'ရည်ရွယ်ချက်နှင့် ပြင်ဆင်မှု (Overview & Setup)',
        timecode: '00:00 - 00:40',
        narration: 'ဒီကနေ့မှာတော့ အချိန်တိုအတွင်းမှာ ကျွမ်းကျင်စွာ ပြုလုပ်နိုင်မယ့် အဆင့်ဆင့် နည်းလမ်းတွေကို အစအဆုံး ရှင်းပြပေးသွားပါမယ်။ စတင်ဖို့အတွက် မရှိမဖြစ် လိုအပ်တဲ့ အခြေခံ အချက် ၃ ချက်ကို အရင်ဆုံး ပြင်ဆင်ထားကြပါမယ်။',
        notes: 'ရှင်းလင်းတိကျသော အသံဖြင့် ပြောကြားရန်။'
      },
      {
        sectionTitle: 'အဆင့် (၁) နှင့် (၂) လုပ်ဆောင်ခြင်း (Steps 1 & 2)',
        timecode: '00:40 - 02:30',
        narration: 'ပထမဦးစွာ Dashboard ကို ဖွင့်ပြီး Create New Project ကို နှိပ်ပါ။ ပြီးရင် Default Setting ထဲကနေ လိုအပ်တဲ့ Parameter တွေကို အခုပြထားတဲ့အတိုင်း ချိန်ညှိပေးရပါမယ်။ လူအများစု မှားတတ်တဲ့ အချက်ကတော့ Cache folder ကို clear မလုပ်ဘဲ ဆက်သွားမိတာပါပဲ။',
        notes: 'မျက်နှာပြင်ပြသမှုနှင့် ကိုက်ညီအောင် ညွှန်ပြပါ။'
      },
      {
        sectionTitle: 'စမ်းသပ်စစ်ဆေးခြင်းနှင့် အကြံပြုချက် (Testing & Pro Tips)',
        timecode: '02:30 - 04:30',
        narration: 'အခုဆိုရင် အားလုံး ပြီးစီးသွားပါပြီ။ စနစ် ကောင်းမွန်စွာ အလုပ်လုပ်ခြင်း ရှိမရှိ စမ်းသပ်ရန် Preview ကို နှိပ်ပြီး စစ်ဆေးနိုင်ပါတယ်။ အဆင်မပြေမှု တစ်စုံတစ်ရာ ရှိပါက အောက်ဖော်ပြပါ Troubleshooting အချက်များကို ပြန်လည်ကြည့်ရှုနိုင်ပါတယ်။',
        notes: 'အားပေးကူညီသည့် လေသံဖြင့် အဆုံးသတ်ပါ။'
      }
    ],
    englishSections: [
      {
        sectionTitle: 'Overview & Prerequisites',
        timecode: '00:00 - 00:40',
        narration: 'In this step-by-step tutorial, you will master the complete workflow in less than five minutes with zero guesswork.',
        notes: 'Clear instructional cadence.'
      },
      {
        sectionTitle: 'Execution: Steps 1 & 2',
        timecode: '00:40 - 02:30',
        narration: 'First, navigate to your workspace settings. Ensure your environment variables are linked properly, and toggle the optimized performance preset.',
        notes: 'Emphasize common pitfalls.'
      },
      {
        sectionTitle: 'Verification & Troubleshooting',
        timecode: '02:30 - 04:30',
        narration: 'Run the quick diagnostic test to confirm everything is synchronized. If you encounter any status errors, follow the troubleshooting checklist shown on screen.',
        notes: 'Supportive tone.'
      }
    ]
  },
  'Tips & Tricks': {
    title: 'လူသိနည်းပြီး အသုံးဝင်လှသော နည်းလမ်းတိုများ (Productivity Tips & Tricks)',
    burmeseSections: [
      {
        sectionTitle: 'အမြန်ဆုံး အကျိုးရှိစေမည့် နည်းလမ်း (Quick Win #1)',
        timecode: '00:00 - 01:10',
        narration: 'သင့်ရဲ့ နေ့စဉ် အလုပ်တွေကို ၂ ဆ ပိုမို မြန်ဆန်စေမယ့် လျှို့ဝှက် shortcut တွေနဲ့ အကြံပြုချက်တွေကို မျှဝေပေးချင်ပါတယ်။ နံပါတ် ၁ နည်းလမ်းကတော့ လူအတော်များများ သတိမထားမိတဲ့ Smart Filter လုပ်ဆောင်ချက်ပဲ ဖြစ်ပါတယ်။',
        notes: 'သွက်လက်တက်ကြွသော လေသံကို သုံးပါ။'
      },
      {
        sectionTitle: 'အချိန်ကုန် သက်သာစေမည့် နည်းစနစ် (Automation Hack #2)',
        timecode: '01:10 - 02:45',
        narration: 'နံပါတ် ၂ ကတော့ အချိန်ကုန် သက်သာစေမယ့် Preset Template တွေ သတ်မှတ်ခြင်းပါ။ ထပ်ခါတလဲလဲ လုပ်ဆောင်ရတဲ့ အဆင့်တွေကို ကလစ်တစ်ချက်တည်းနဲ့ အလိုအလျောက် ပြီးမြောက်စေနိုင်ပါတယ်။',
        notes: 'လက်တွေ့ အသုံးဝင်မှုကို ထင်ဟပ်စေပါ။'
      },
      {
        sectionTitle: 'နောက်ဆုံး အဆင့်မြင့် အကြံပြုချက် (Pro Secret #3)',
        timecode: '02:45 - 04:00',
        narration: 'နံပါတ် ၃ လျှို့ဝှက်ချက်ကတော့ အထူးဆုံးပါပဲ။ ဒီ feature လေးကို On ထားလိုက်တာနဲ့ မလိုအပ်တဲ့ background process တွေကို ရပ်တန့်ပေးပြီး စက်စွမ်းဆောင်ရည်ကို ချက်ချင်း မြှင့်တင်ပေးနိုင်ပါတယ်။',
        notes: 'အံ့အားသင့်ဖွယ် ခံစားချက်ကို ဖော်ပြပါ။'
      }
    ],
    englishSections: [
      {
        sectionTitle: 'Tip 1: The Hidden Shortcut',
        timecode: '00:00 - 01:10',
        narration: 'Here is the first game-changing trick that will immediately double your daily output without complicated configurations.',
        notes: 'Fast and snappy.'
      },
      {
        sectionTitle: 'Tip 2: Workflow Automation',
        timecode: '01:10 - 02:45',
        narration: 'Instead of repetitive manual steps, build reusable quick presets to automate repetitive tasks in one single tap.',
        notes: 'Highlight time savings.'
      },
      {
        sectionTitle: 'Tip 3: The Secret Power Setting',
        timecode: '02:45 - 04:00',
        narration: 'Most users overlook this toggle in advanced options, but turning it on boosts responsiveness dramatically.',
        notes: 'Deliver with enthusiasm.'
      }
    ]
  },
  'Educational': {
    title: 'သိပ္ပံနှင့် သမိုင်းကြောင်းဆိုင်ရာ ရှင်းလင်းချက် (In-Depth Educational Study)',
    burmeseSections: [
      {
        sectionTitle: 'အခြေခံ အယူအဆ မိတ်ဆက် (Core Concept)',
        timecode: '00:00 - 01:00',
        narration: 'လူသားတွေရဲ့ သမိုင်းတစ်လျှောက်မှာ စူးစမ်းရှာဖွေလိုစိတ်ဟာ အကြီးမားဆုံးသော ရှာဖွေတွေ့ရှိမှုတွေကို ဖန်တီးပေးခဲ့ပါတယ်။ ဒီနေ့မှာတော့ စကြဝဠာရဲ့ လျှို့ဝှက်နက်နဲမှုနဲ့ ရူပဗေဒ အခြေခံ သဘောတရားတွေကို ရိုးရှင်းစွာ လေ့လာသွားပါမယ်။',
        notes: 'တည်ငြိမ်လေးနက်သော ဆရာသဖွယ် လေသံဖြင့် ဖတ်ရှုပါ။'
      },
      {
        sectionTitle: 'သဘာဝတရား၏ နိယာမများ (Fundamental Laws)',
        timecode: '01:00 - 03:00',
        narration: 'ဒြပ်ဆွဲအားနိယာမနဲ့ အချိန်-အာကာသ (Spacetime) ရဲ့ ဆက်စပ်မှုကို စတင် နားလည်လာတဲ့အခါ ဂြိုဟ်တွေရဲ့ လည်ပတ်မှုဟာ ဘာကြောင့် ဒီလို ဖြစ်နေရသလဲဆိုတာ ရှင်းလင်းလာပါတယ်။ အိုင်းစတိုင်းရဲ့ နှိုင်းရသီအိုရီက ဒီအချက်ကို အခိုင်အမာ သက်သေပြခဲ့ပါတယ်။',
        notes: 'ခက်ခဲသော သဘောတရားများကို ဥပမာများနှင့် တွဲဖက်ပြောပါ။'
      },
      {
        sectionTitle: 'အကျိုးသက်ရောက်မှုနှင့် သုတေသန (Modern Implications)',
        timecode: '03:00 - 05:00',
        narration: 'ယနေ့ခေတ် GPS စနစ်တွေနဲ့ ဂြိုဟ်တုဆက်သွယ်ရေးတွေဟာ ဒီရူပဗေဒ တွက်ချက်မှုတွေ မပါရင် တိကျစွာ အလုပ်လုပ်နိုင်မှာ မဟုတ်ပါဘူး။ အခြေခံ သိပ္ပံပညာရဲ့ အရေးပါမှုကို ဒီနေရာမှာ ထင်ရှားစွာ တွေ့မြင်နိုင်ပါတယ်။',
        notes: 'အသိဉာဏ်ပွင့်လင်းစေမည့် နိဂုံးစကား။'
      }
    ],
    englishSections: [
      {
        sectionTitle: 'Foundational Principles',
        timecode: '00:00 - 01:00',
        narration: 'Throughout history, human curiosity has propelled the greatest leaps in understanding our universe and physical laws.',
        notes: 'Thoughtful and authoritative.'
      },
      {
        sectionTitle: 'Mechanisms and Evidence',
        timecode: '01:00 - 03:00',
        narration: 'By examining how spacetime curves around massive bodies, general relativity explained planetary anomalies that classical mechanics could not.',
        notes: 'Explain conceptually.'
      },
      {
        sectionTitle: 'Modern Technological Applications',
        timecode: '03:00 - 05:00',
        narration: 'Today, everyday technologies like GPS navigation rely directly on relativistic time dilation calculations to maintain pinpoint accuracy.',
        notes: 'Inspiring takeaway.'
      }
    ]
  },
  'General Explanation': {
    title: 'ပြည့်စုံသော အကြောင်းအရာ ရှင်းလင်းတင်ပြချက် (Comprehensive Breakdown)',
    burmeseSections: [
      {
        sectionTitle: 'အကြောင်းအရာ အနှစ်ချုပ် (Overview)',
        timecode: '00:00 - 00:45',
        narration: 'ဒီဗီဒီယိုမှာတော့ လူတိုင်း သိသင့်သိထိုက်တဲ့ အကြောင်းအရာတစ်ခုကို ရှင်းလင်းလွယ်ကူတဲ့ စကားလုံးတွေနဲ့ အစအဆုံး အကျဉ်းချုပ် ရှင်းပြပေးသွားမှာ ဖြစ်ပါတယ်။',
        notes: 'လူတိုင်း နားလည်နိုင်သော ရိုးရှင်းသော အသုံးအနှုန်းကို အသုံးပြုပါ။'
      },
      {
        sectionTitle: 'အဓိက အကြောင်းရင်းများနှင့် နောက်ခံ (Key Drivers & Background)',
        timecode: '00:45 - 02:45',
        narration: 'ဒီကိစ္စရပ်ရဲ့ နောက်ကွယ်မှာ အဓိက အကြောင်းရင်း ၃ ခု ရှိပါတယ်။ ပထမတစ်ခုကတော့ လူမှုစီးပွား ပြောင်းလဲမှုတွေဖြစ်ပြီး ဒုတိယအချက်ကတော့ ဈေးကွက် လိုအပ်ချက် တိုးတက်လာခြင်းပဲ ဖြစ်ပါတယ်။',
        notes: 'အချက်အလက်များကို အစဉ်လိုက် တင်ပြပါ။'
      },
      {
        sectionTitle: 'အနာဂတ် သုံးသပ်ချက် (Future Outlook)',
        timecode: '02:45 - 04:30',
        narration: 'ရှေ့လာမယ့် ကာလတွေမှာ ဘယ်လို ဆက်လက်ဖြစ်ပေါ်လာနိုင်သလဲဆိုတာကို ကြိုတင်ခန့်မှန်းချက်တွေနဲ့အတူ အကျဉ်းချုပ် ကောက်ချက်ဆွဲပေးထားပါတယ်။',
        notes: 'အမြင်သစ်ရစေမည့် သုံးသပ်ချက်။'
      }
    ],
    englishSections: [
      {
        sectionTitle: 'Executive Overview',
        timecode: '00:00 - 00:45',
        narration: 'In this breakdown, we demystify the core fundamentals in clear, accessible terms so anyone can understand the bigger picture.',
        notes: 'Approachable tone.'
      },
      {
        sectionTitle: 'Key Factors & Context',
        timecode: '00:45 - 02:45',
        narration: 'Three primary catalysts have accelerated this trend: shifting consumer behavior, technological readiness, and reduced friction.',
        notes: 'Structured delivery.'
      },
      {
        sectionTitle: 'Summary & Forecast',
        timecode: '02:45 - 04:30',
        narration: 'Looking ahead into the next quarters, expect consolidation and deeper integration across everyday workflows.',
        notes: 'Clear concluding perspective.'
      }
    ]
  }
};

export function generateMockResult(
  url: string,
  contentType: ContentType,
  narrationStyle: NarrationStyle,
  scriptLength: ScriptLength,
  language: OutputLanguage
): GeneratedResult {
  const template = mockTemplates[contentType] || mockTemplates['Technology'];
  const sections = language === 'Burmese' ? template.burmeseSections : template.englishSections;

  // Filter or scale sections based on script length
  let filteredSections = [...sections];
  if (scriptLength === '1 minute') {
    filteredSections = [
      {
        sectionTitle: sections[0].sectionTitle,
        timecode: '00:00 - 00:20',
        narration: sections[0].narration.slice(0, 140) + '...',
        notes: 'Short hook format.'
      },
      {
        sectionTitle: 'အဓိက အကျဉ်းချုပ် (Quick Takeaway)',
        timecode: '00:20 - 01:00',
        narration: sections[1].narration.slice(0, 160) + '...',
        notes: 'Fast paced 60-second summary.'
      }
    ];
  } else if (scriptLength === 'Detailed') {
    // Add extra detailed notes
    filteredSections = sections.map((sec, idx) => ({
      ...sec,
      narration: `${sec.narration}\n\n[အသေးစိတ် ဖြည့်စွက်ချက် / Extra Detail]: အချက်အလက်များနှင့် သက်သေအထောက်အထားများအရ ဤအဆင့်တွင် ပိုမိုနက်နဲစွာ နားလည်သဘောပေါက်စေရန် အထူးဂရုပြု၍ စီစဉ်ထားခြင်းဖြစ်ပါသည်။`,
      notes: `Section ${idx + 1} - Style: ${narrationStyle}. Optimized for high retention.`
    }));
  }

  const fullText = filteredSections
    .map(s => `[${s.sectionTitle} - ${s.timecode || '00:00'}]\n${s.narration}\n(Note: ${s.notes || ''})`)
    .join('\n\n');

  const charCount = fullText.length;
  // Estimate words: rough word count for Burmese/English
  const wordCount = fullText.split(/\s+/).filter(Boolean).length;

  return {
    title: template.title,
    contentType,
    narrationStyle,
    scriptLength,
    language,
    videoUrl: url,
    characterCount: charCount,
    wordCount: wordCount,
    estimatedDuration: scriptLength === '1 minute' ? '1:00' : scriptLength === '5 minutes' ? '4:45' : scriptLength === '10 minutes' ? '9:50' : '14:20',
    fullText,
    sections: filteredSections,
    generatedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };
}

export const sampleVideos = [
  {
    title: 'Top 10 AI Tools Revolutionizing Content Creation in 2026',
    url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    type: 'Technology' as ContentType,
    duration: '12:45'
  },
  {
    title: 'The Cyberpunk Mystery Explained: Plot Twists & Ending',
    url: 'https://www.youtube.com/watch?v=kXYiU_JCYtU',
    type: 'Movie Recap' as ContentType,
    duration: '18:20'
  },
  {
    title: 'Build a Complete Full-Stack Web App in 10 Minutes',
    url: 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
    type: 'Tutorial / How-to' as ContentType,
    duration: '10:15'
  }
];
