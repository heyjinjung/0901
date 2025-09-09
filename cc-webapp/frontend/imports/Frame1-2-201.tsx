function ColorBackgroundDarkNavy() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Background/Dark Navy"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-slate-900 rounded shrink-0 size-16"
          data-name="Background/Dark Navy"
        />
        <div className="font-['Exo:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[16px] text-left text-nowrap text-slate-100">
          <p className="block leading-[28px] whitespace-pre">#1a1a1a</p>
        </div>
      </div>
    </div>
  );
}

function ColorBackgroundCharcoal() {
  return (
    <div
      className="bg-[#2d2d2d] relative shrink-0"
      data-name="Color/Background/Charcoal"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-slate-800 rounded shrink-0 size-16"
          data-name="Background/Charcoal"
        />
        <div className="font-['Exo:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[16px] text-left text-nowrap text-slate-100">
          <p className="block leading-[28px] whitespace-pre">#2d2d2d</p>
        </div>
      </div>
    </div>
  );
}

function PrimarySwatches() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Primary/Swatches"
    >
      <div className="box-border content-stretch flex flex-row gap-4 items-center justify-start overflow-clip p-0 relative">
        <ColorBackgroundDarkNavy />
        <ColorBackgroundCharcoal />
      </div>
    </div>
  );
}

function Primary() {
  return (
    <div
      className="absolute bg-[#1a1a1a] left-[57.615px] top-[104px] w-[193.769px]"
      data-name="Primary"
    >
      <div className="overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-col gap-2 items-start justify-start p-[16px] relative w-[193.769px]">
          <div className="font-['Exo:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[16px] text-left text-nowrap text-slate-100">
            <p className="block leading-[28px] whitespace-pre">Primary</p>
          </div>
          <PrimarySwatches />
        </div>
      </div>
    </div>
  );
}

function ColorTextPrimaryWhite() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Text/Primary White"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-slate-100 rounded shrink-0 size-16"
          data-name="Text/Primary White"
        />
        <div className="font-['IBM_Plex_Sans_KR:Bold',_sans-serif] leading-[0] not-italic relative shrink-0 text-[#ffffff] text-[14px] text-left text-nowrap">
          <p className="block leading-[28px] whitespace-pre">#FFFFFF</p>
        </div>
      </div>
    </div>
  );
}

function ColorTextSecondaryGray() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Text/Secondary Gray"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-gray-300 rounded shrink-0 size-16"
          data-name="Text/Secondary Gray"
        />
        <div className="font-['IBM_Plex_Sans_KR:Bold',_sans-serif] leading-[0] not-italic relative shrink-0 text-[14px] text-gray-300 text-left text-nowrap">
          <p className="block leading-[28px] whitespace-pre">#D1D5DB</p>
        </div>
      </div>
    </div>
  );
}

function TextSwatches() {
  return (
    <div className="bg-[#1a1a1a] relative shrink-0" data-name="Text/Swatches">
      <div className="box-border content-stretch flex flex-row gap-4 items-center justify-start overflow-clip p-0 relative">
        <ColorTextPrimaryWhite />
        <ColorTextSecondaryGray />
      </div>
    </div>
  );
}

function Text() {
  return (
    <div
      className="absolute bg-[#1a1a1a] left-[75.231px] top-[265px] w-[158.538px]"
      data-name="Text"
    >
      <div className="box-border content-stretch flex flex-col gap-2 items-start justify-start overflow-clip p-0 relative w-[158.538px]">
        <div className="font-['IBM_Plex_Sans_KR:Bold',_sans-serif] leading-[0] not-italic relative shrink-0 text-[14px] text-left text-nowrap text-slate-100">
          <p className="block leading-[28px] whitespace-pre">Text</p>
        </div>
        <TextSwatches />
      </div>
    </div>
  );
}

function ColorAccentCyan() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Accent/Cyan"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-[#ff4516] rounded shrink-0 size-16"
          data-name="Accent/Cyan"
        />
        <div className="font-['Exo:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[16px] text-left text-nowrap text-slate-100">
          <p className="block leading-[28px] whitespace-pre">#ff4516</p>
        </div>
      </div>
    </div>
  );
}

function ColorAccentWarmAmber() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Accent/Warm Amber"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-amber-500 rounded shrink-0 size-16"
          data-name="Accent/Warm Amber"
        />
        <div className="font-['Exo:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[16px] text-left text-nowrap text-slate-100">
          <p className="block leading-[28px] whitespace-pre">#F59E0B</p>
        </div>
      </div>
    </div>
  );
}

function AccentSwatches() {
  return (
    <div className="bg-[#1a1a1a] relative shrink-0" data-name="Accent/Swatches">
      <div className="box-border content-stretch flex flex-row gap-4 items-center justify-start overflow-clip p-0 relative">
        <ColorAccentCyan />
        <ColorAccentWarmAmber />
      </div>
    </div>
  );
}

function Accent() {
  return (
    <div
      className="absolute bg-[#1a1a1a] left-[75.231px] top-[394px] w-[158.538px]"
      data-name="Accent"
    >
      <div className="box-border content-stretch flex flex-col gap-2 items-start justify-start overflow-clip p-0 relative w-[158.538px]">
        <div className="font-['Exo:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[16px] text-left text-nowrap text-slate-100">
          <p className="block leading-[28px] whitespace-pre">Accent</p>
        </div>
        <AccentSwatches />
      </div>
    </div>
  );
}

function ColorNeutralLightGray() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Neutral/Light Gray"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-[#e0e0e0] rounded shrink-0 size-16"
          data-name="Neutral/Light Gray"
        />
        <div className="font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[14px] text-left text-nowrap text-slate-100">
          <p className="block leading-[18.9px] whitespace-pre">E0E0E0</p>
        </div>
      </div>
    </div>
  );
}

function ColorNeutralMediumGray() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Neutral/Medium Gray"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-[#a0a0a0] rounded shrink-0 size-16"
          data-name="Neutral/Medium Gray"
        />
        <div className="font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[14px] text-left text-nowrap text-slate-100">
          <p className="block leading-[18.9px] whitespace-pre">A0A0A0</p>
        </div>
      </div>
    </div>
  );
}

function ColorNeutralDarkGray() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Neutral/Dark Gray"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-[#333333] rounded shrink-0 size-16"
          data-name="Neutral/Dark Gray"
        />
        <div className="font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[14px] text-left text-nowrap text-slate-100">
          <p className="block leading-[18.9px] whitespace-pre">333333</p>
        </div>
      </div>
    </div>
  );
}

function NeutralSwatches() {
  return (
    <div
      className="bg-[#1a1a1a] relative shrink-0"
      data-name="Neutral/Swatches"
    >
      <div className="box-border content-stretch flex flex-row gap-4 items-center justify-start overflow-clip p-0 relative">
        <ColorNeutralLightGray />
        <ColorNeutralMediumGray />
        <ColorNeutralDarkGray />
      </div>
    </div>
  );
}

function Neutral() {
  return (
    <div
      className="absolute bg-[#1a1a1a] left-10 top-[523px] w-[229px]"
      data-name="Neutral"
    >
      <div className="box-border content-stretch flex flex-col gap-2 items-start justify-start overflow-clip p-0 relative w-[229px]">
        <div className="font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[14px] text-left text-nowrap text-slate-100">
          <p className="block leading-[18.9px] whitespace-pre">Neutral</p>
        </div>
        <NeutralSwatches />
      </div>
    </div>
  );
}

function ColorSemanticSuccess() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Semantic/Success"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-emerald-500 rounded shrink-0 size-16"
          data-name="Semantic/Success"
        />
        <div className="font-['Exo:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[16px] text-left text-nowrap text-slate-100">
          <p className="block leading-[28px] whitespace-pre">#10B981</p>
        </div>
      </div>
    </div>
  );
}

function ColorSemanticError() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Semantic/Error"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-[#b90c29] rounded shrink-0 size-16"
          data-name="Semantic/Error"
        />
        <div className="font-['Exo:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[16px] text-left text-nowrap text-slate-100">
          <p className="block leading-[28px] whitespace-pre">B90C29</p>
        </div>
      </div>
    </div>
  );
}

function ColorSemanticInfo() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Color/Semantic/Info"
    >
      <div className="box-border content-stretch flex flex-col gap-1 items-center justify-start overflow-clip p-0 relative">
        <div
          className="bg-[#135b79] rounded shrink-0 size-16"
          data-name="Semantic/Info"
        />
        <div className="font-['Exo:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[16px] text-left text-nowrap text-slate-100">
          <p className="block leading-[28px] whitespace-pre">135B79</p>
        </div>
      </div>
    </div>
  );
}

function SemanticSwatches() {
  return (
    <div
      className="bg-slate-900 relative shrink-0"
      data-name="Semantic/Swatches"
    >
      <div className="box-border content-stretch flex flex-row gap-4 items-center justify-start overflow-clip p-0 relative">
        <ColorSemanticSuccess />
        <ColorSemanticError />
        <ColorSemanticInfo />
      </div>
    </div>
  );
}

function Semantic() {
  return (
    <div
      className="absolute bg-[#1a1a1a] left-10 top-[652px] w-[229px]"
      data-name="Semantic"
    >
      <div className="box-border content-stretch flex flex-col gap-2 items-start justify-start overflow-clip p-0 relative w-[229px]">
        <div className="font-['Exo:Regular',_sans-serif] font-normal leading-[0] relative shrink-0 text-[16px] text-left text-nowrap text-slate-100">
          <p className="block leading-[28px] whitespace-pre">Semantic</p>
        </div>
        <SemanticSwatches />
      </div>
    </div>
  );
}

function Component1Colors() {
  return (
    <div className="absolute contents left-10 top-8" data-name="1. Colors">
      <div
        className="absolute capitalize font-['Exo:Bold',_sans-serif] font-bold leading-[0] text-[32px] text-center text-slate-100 top-8 translate-x-[-50%] w-[229px]"
        style={{ left: "calc(50% - 3.5px)" }}
      >
        <p className="block leading-[28px]">1. COLOR PALETTE</p>
      </div>
      <Primary />
      <Text />
      <Accent />
      <Neutral />
      <Semantic />
    </div>
  );
}

function Frame2() {
  return (
    <div className="absolute h-[87px] left-10 top-[817px] w-56">
      <div className="box-border grid grid-cols-[repeat(4,_minmax(0px,_1fr))] grid-rows-[repeat(1,_minmax(0px,_1fr))] h-[87px] p-0 relative w-56">
        <div className="[grid-area:1_/_1] bg-[#7b29cd] h-16 shrink-0" />
        <div className="[grid-area:1_/_2] bg-[#870dd1] h-16 shrink-0" />
        <div className="[grid-area:1_/_3] bg-[#5b30f6] h-16 shrink-0" />
        <div className="[grid-area:1_/_4] bg-[#8054f2] h-16 shrink-0" />
      </div>
    </div>
  );
}

export default function Frame1() {
  return (
    <div className="bg-[#1e1e1e] relative size-full">
      <Component1Colors />
      <Frame2 />
    </div>
  );
}