import { GameDashboardGame } from '../types';

// 🎯 난이도별 색상 반환
export const getDifficultyColor = (difficulty: string): string => {
  switch (difficulty) {
    case 'Easy': return 'text-success';
    case 'Medium': return 'text-warning';
    case 'Hard': return 'text-error';
    case 'Extreme': return 'text-gradient-primary';
    default: return 'text-muted-foreground';
  }
};

// 🎮 게임 네비게이션 처리
export const createGameNavigator = (
  games: GameDashboardGame[],
  userGoldBalance: number,
  onAddNotification: (message: string) => void,
  navigationHandlers: {
    onNavigateToSlot: () => void;
    onNavigateToRPS: () => void;
    onNavigateToGacha: () => void;
    onNavigateToCrash: () => void;
  }
) => {
  return (gameId: string) => {
    const game = games.find(g => g.id === gameId);
    if (!game) return;

    if (userGoldBalance < game.cost) {
      onAddNotification(`💰 골드가 부족합니다! (필요: ${game.cost}G)`);
      return;
    }

    switch (gameId) {
      case 'slot':
        navigationHandlers.onNavigateToSlot();
        break;
      case 'rps':
        navigationHandlers.onNavigateToRPS();
        break;
      case 'gacha':
        navigationHandlers.onNavigateToGacha();
        break;
      case 'crash':
        navigationHandlers.onNavigateToCrash();
        break;
    }
  };
};

// 🌐 외부 링크 네비게이션
export const handleModelNavigation = () => {
  window.open('https://md-01.com', '_blank');
};