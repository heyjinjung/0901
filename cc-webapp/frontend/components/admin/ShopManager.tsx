'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Search,
  Edit,
  Trash2,
  Eye,
  EyeOff,
  Filter,
  Download,
  Upload,
  Save,
  X,
  Package,
  DollarSign,
  TrendingUp,
  Tag,
  Image as ImageIcon,
} from 'lucide-react';
import { ShopItem } from '../../types/admin';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { Switch } from '../ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
  import { Label } from '../ui/Label';
import { api } from '@/lib/unifiedApi';
import { useWithReconcile } from '@/lib/sync';

interface ShopManagerProps {
  onAddNotification: (message: string) => void;
}

export function ShopManager({ onAddNotification }: ShopManagerProps) {
  const [shopItems, setShopItems] = useState([] as ShopItem[]);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all' as string);
  const [includeDeleted, setIncludeDeleted] = useState(false as boolean);
  const [showCreateModal, setShowCreateModal] = useState(false as boolean);
  const [editingItem, setEditingItem] = useState(null as ShopItem | null);
  const [isLoading, setIsLoading] = useState(false as boolean);
  const withReconcile = useWithReconcile();
  // NOTE(2025-08-29): Admin Shop API 표준화
  // - 프론트는 /api/shop/admin/products 네임스페이스를 기준으로 사용합니다.
  // - 백엔드에는 /api/admin/shop/items 도 공존하나, 중복 제거 정책에 따라 폐기 예정 경로로 간주합니다.
  // - 필드 스키마도 상이(AdminCatalogItem* vs products): 현재 컴포넌트는 products 스키마에 맞춰 동작합니다.
  // Load products from backend
  const load = useCallback(async () => {
    try {
      // GET /api/shop/admin/products?include_deleted=bool (표준)
      const list = await api.get<any[]>(`shop/admin/products${includeDeleted ? '?include_deleted=true' : ''}`);
      // Map backend → UI type
      const mapped: ShopItem[] = (list || []).map((p: any) => {
        const extra = p.extra || {};
        return {
          id: String(p.product_id || p.id || ''),
          name: String(p.name || ''),
          description: String(p.description || ''),
          price: Number(p.price || 0),
          category: String(extra.category || 'skin'),
          rarity: String(extra.rarity || 'common'),
          isActive: Boolean(p.is_active ?? (p.deleted_at ? false : true)),
          stock: extra.stock !== undefined ? Number(extra.stock) : undefined,
          discount: extra.discount !== undefined ? Number(extra.discount) : undefined,
          icon: String(extra.icon || '📦'),
          createdAt: p.created_at ? new Date(p.created_at) : new Date(),
          updatedAt: p.updated_at ? new Date(p.updated_at) : new Date(),
          sales: Number(p.sales || 0),
          tags: Array.isArray(extra.tags) ? extra.tags : [],
        } as ShopItem;
      });
      setShopItems(mapped);
    } catch (e: any) {
      onAddNotification(`상점 목록 로드 실패: ${e.message || e}`);
    }
  }, [onAddNotification, includeDeleted]);

  useEffect(() => { load(); }, [load]);

  // Filter items
  const filteredItems = shopItems.filter((item: ShopItem) => {
    const matchesSearch =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.tags.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCategory = categoryFilter === 'all' || item.category === categoryFilter;
    const matchesActive = includeDeleted ? true : item.isActive;
    return matchesSearch && matchesCategory && matchesActive;
  });

  // Handle create/edit item
  const handleSaveItem = async (itemData: Partial<ShopItem> & { product_id?: string }) => {
    setIsLoading(true);

    try {
      if (editingItem) {
        // PUT /api/shop/admin/products/{product_id}
        await withReconcile(async () => {
          await api.put(`shop/admin/products/${encodeURIComponent(editingItem.id)}`, {
            name: itemData.name,
            price: itemData.price,
            description: itemData.description,
            is_active: itemData.isActive,
            extra: {
              category: itemData.category,
              rarity: itemData.rarity,
              stock: itemData.stock,
              discount: itemData.discount,
              icon: itemData.icon,
              tags: itemData.tags,
            },
          });
          return {} as any;
        });
        onAddNotification(`✅ "${itemData.name}" 아이템이 수정되었습니다.`);
      } else {
        // POST /api/shop/admin/products
        if (!itemData.product_id || !itemData.name) {
          throw new Error('product_id와 name은 필수입니다.');
        }
        await withReconcile(async () => {
          await api.post(`shop/admin/products`, {
            product_id: itemData.product_id,
            name: itemData.name,
            price: itemData.price ?? 0,
            description: itemData.description,
            extra: {
              category: itemData.category,
              rarity: itemData.rarity,
              stock: itemData.stock,
              discount: itemData.discount,
              icon: itemData.icon,
              tags: itemData.tags,
            },
          });
          return {} as any;
        });
        onAddNotification(`✅ "${itemData.name}" 아이템이 생성되었습니다.`);
      }

      setShowCreateModal(false);
      setEditingItem(null);
      await load();
    } catch (error) {
      onAddNotification('❌ 아이템 저장에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle delete item
  const handleDeleteItem = async (itemId: string) => {
    if (!confirm('정말로 이 아이템을 삭제하시겠습니까?')) return;

    setIsLoading(true);

    try {
      await withReconcile(async () => {
        await api.del(`shop/admin/products/${encodeURIComponent(itemId)}`);
        return {} as any;
      });
      await load();
      onAddNotification('🗑️ 아이템이 삭제되었습니다.');
      // emitEvent('shopCatalogUpdated', { source: 'admin' }); // TODO: 이벤트 시스템 구현 시 활성화
    } catch (error) {
      onAddNotification('❌ 아이템 삭제에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle item active status
  const toggleItemStatus = async (itemId: string) => {
    const target = shopItems.find((i: ShopItem) => i.id === itemId);
    if (!target) return;
    setIsLoading(true);
    try {
      // If currently active, soft delete; else restore
      if (target.isActive) {
        await withReconcile(async () => {
          await api.del(`shop/admin/products/${encodeURIComponent(itemId)}`);
          return {} as any;
        });
      } else {
        await withReconcile(async () => {
          await api.post(`shop/admin/products/${encodeURIComponent(itemId)}/restore`, {});
          return {} as any;
        });
      }
      await load();
      onAddNotification(`${target.isActive ? '⏸️' : '▶️'} "${target.name}" 상태가 변경되었습니다.`);
    } catch (e) {
      onAddNotification('❌ 상태 변경에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // Get rarity color
  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common':
        return 'text-muted-foreground';
      case 'rare':
        return 'text-info';
      case 'epic':
        return 'text-primary';
      case 'legendary':
        return 'text-gold';
      case 'mythic':
        return 'text-gradient-primary';
      default:
        return 'text-muted-foreground';
    }
  };

  const categories = [
    { value: 'skin', label: '스킨' },
    { value: 'powerup', label: '파워업' },
    { value: 'currency', label: '화폐' },
    { value: 'collectible', label: '수집품' },
    { value: 'character', label: '캐릭터' },
    { value: 'weapon', label: '무기' },
  ];

  const rarities = [
    { value: 'common', label: '일반' },
    { value: 'rare', label: '희귀' },
    { value: 'epic', label: '영웅' },
    { value: 'legendary', label: '전설' },
    { value: 'mythic', label: '신화' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">상점 관리</h2>
          <p className="text-muted-foreground">아이템 추가, 수정, 삭제 및 재고 관리</p>
        </div>

        <div className="flex gap-3">
          <Button variant="outline" className="btn-hover-lift">
            <Download className="w-4 h-4 mr-2" />
            내보내기
          </Button>
          <Button variant="outline" className="btn-hover-lift">
            <Upload className="w-4 h-4 mr-2" />
            가져오기
          </Button>
          <Button
            onClick={() => setShowCreateModal(true)}
            className="bg-gradient-game btn-hover-lift"
          >
            <Plus className="w-4 h-4 mr-2" />
            아이템 추가
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-soft rounded-lg flex items-center justify-center">
                <Package className="w-5 h-5 text-primary" />
              </div>
              <div>
                <div className="text-lg font-bold text-foreground">{shopItems.length}</div>
                <div className="text-sm text-muted-foreground">총 아이템</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-success-soft rounded-lg flex items-center justify-center">
                <Eye className="w-5 h-5 text-success" />
              </div>
              <div>
                <div className="text-lg font-bold text-foreground">
                  {shopItems.filter((item: ShopItem) => item.isActive).length}
                </div>
                <div className="text-sm text-muted-foreground">활성 아이템</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gold-soft rounded-lg flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-gold" />
              </div>
              <div>
                <div className="text-lg font-bold text-foreground">
                  {shopItems
                    .reduce((sum: number, item: ShopItem) => sum + item.sales * item.price, 0)
                    .toLocaleString()}
                  G
                </div>
                <div className="text-sm text-muted-foreground">총 매출</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-info-soft rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-info" />
              </div>
              <div>
                <div className="text-lg font-bold text-foreground">
                  {shopItems
                    .reduce((sum: number, item: ShopItem) => sum + item.sales, 0)
                    .toLocaleString()}
                </div>
                <div className="text-sm text-muted-foreground">총 판매량</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col lg:flex-row gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="아이템 검색..."
            value={searchQuery}
            onChange={(e: React.FormEvent<HTMLInputElement>) =>
              setSearchQuery((e.currentTarget as HTMLInputElement).value)
            }
            className="pl-10"
          />
        </div>

        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="카테고리" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체 카테고리</SelectItem>
            {categories.map((category) => (
              <SelectItem key={category.value} value={category.value}>
                {category.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="flex items-center gap-2 pl-2">
          <Switch checked={includeDeleted} onCheckedChange={setIncludeDeleted} />
          <span className="text-sm text-muted-foreground">삭제/비활성 포함</span>
        </div>
      </div>

      {/* Items Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredItems.map((item: ShopItem, index: number) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-effect rounded-xl p-6 card-hover-float"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="text-3xl">{item.icon}</div>
                <div>
                  <h3 className="font-bold text-foreground">{item.name}</h3>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </div>
              </div>

              <Switch checked={item.isActive} onCheckedChange={() => toggleItemStatus(item.id)} />
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">가격</span>
                <div className="flex items-center gap-2">
                  {item.discount && (
                    <span className="text-xs text-error line-through">
                      {item.price.toLocaleString()}G
                    </span>
                  )}
                  <span className="font-bold text-gold">
                    {Math.floor(item.price * (1 - (item.discount || 0) / 100)).toLocaleString()}G
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">희귀도</span>
                <Badge className={getRarityColor(item.rarity)}>
                  {rarities.find((r) => r.value === item.rarity)?.label}
                </Badge>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">판매량</span>
                <span className="font-medium text-foreground">{item.sales.toLocaleString()}</span>
              </div>

              {item.stock !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">재고</span>
                  <span
                    className={`font-medium ${item.stock < 10 ? 'text-error' : 'text-foreground'}`}
                  >
                    {item.stock}
                  </span>
                </div>
              )}

              {item.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {item.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {item.tags.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{item.tags.length - 3}
                    </Badge>
                  )}
                </div>
              )}
            </div>

            <div className="flex gap-2 mt-4 pt-4 border-t border-border-secondary">
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setEditingItem(item);
                  setShowCreateModal(true);
                }}
                className="flex-1"
              >
                <Edit className="w-4 h-4 mr-1" />
                수정
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleDeleteItem(item.id)}
                className="border-error text-error hover:bg-error hover:text-white"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Create/Edit Modal */}
      <ItemModal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setEditingItem(null);
        }}
        onSave={handleSaveItem}
        editingItem={editingItem}
        isLoading={isLoading}
        categories={categories}
        rarities={rarities}
      />
    </div>
  );
}

// Item Modal Component
interface ItemModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (itemData: Partial<ShopItem>) => void;
  editingItem: ShopItem | null;
  isLoading: boolean;
  categories: Array<{ value: string; label: string }>;
  rarities: Array<{ value: string; label: string }>;
}

function ItemModal({ 
  isOpen, 
  onClose, 
  onSave, 
  editingItem, 
  isLoading, 
  categories, 
  rarities 
}: ItemModalProps) {
  const [formData, setFormData] = useState({
  product_id: '',
    name: '',
    description: '',
    price: 0,
    category: 'skin',
    rarity: 'common',
    isActive: true,
    icon: '📦',
    tags: []
  } as Partial<ShopItem>);

  useEffect(() => {
    if (editingItem) {
      // Map editing item to form (no product_id change allowed)
      setFormData({
        name: editingItem.name,
        description: editingItem.description,
        price: editingItem.price,
        category: editingItem.category,
        rarity: editingItem.rarity,
        isActive: editingItem.isActive,
        icon: editingItem.icon,
        tags: editingItem.tags,
      });
    } else {
      setFormData({
        product_id: '',
        name: '',
        description: '',
        price: 0,
        category: 'skin',
        rarity: 'common',
        isActive: true,
        icon: '📦',
        tags: []
      });
    }
  }, [editingItem, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          onClick={(e: any) => e.stopPropagation()}
          className="glass-effect rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-foreground">
              {editingItem ? '아이템 수정' : '새 아이템 추가'}
            </h3>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {!editingItem && (
                <div>
                  <Label htmlFor="product_id">상품 ID (고유) *</Label>
                  <Input
                    id="product_id"
                    value={(formData as any).product_id || ''}
                    onChange={(e: any) => setFormData((prev: Partial<ShopItem>) => ({ ...prev, product_id: e.target.value as any }))}
                    placeholder="ex) skin_gold_001"
                    required
                  />
                </div>
              )}
              <div>
                <Label htmlFor="name">아이템 이름 *</Label>
                <Input
                  id="name"
                  value={formData.name || ''}
                  onChange={(e: any) => setFormData((prev: Partial<ShopItem>) => ({ ...prev, name: e.target.value }))}
                  placeholder="아이템 이름을 입력하세요"
                  required
                />
              </div>

              <div>
                <Label htmlFor="icon">아이콘 *</Label>
                <Input
                  id="icon"
                  value={formData.icon || ''}
                  onChange={(e: any) => setFormData((prev: Partial<ShopItem>) => ({ ...prev, icon: e.target.value }))}
                  placeholder="📦"
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="description">설명</Label>
              <Textarea
                id="description"
                value={formData.description || ''}
                onChange={(e: any) => setFormData((prev: Partial<ShopItem>) => ({ ...prev, description: e.target.value }))}
                placeholder="아이템 설명을 입력하세요"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="price">가격 (골드) *</Label>
                <Input
                  id="price"
                  type="number"
                  value={formData.price || 0}
                  onChange={(e: any) => setFormData((prev: Partial<ShopItem>) => ({ ...prev, price: parseInt(e.target.value) || 0 }))}
                  placeholder="0"
                  min="0"
                  required
                />
              </div>

              <div>
                <Label htmlFor="stock">재고 (선택)</Label>
                <Input
                  id="stock"
                  type="number"
                  value={formData.stock || ''}
                  onChange={(e: any) => setFormData((prev: Partial<ShopItem>) => ({ ...prev, stock: e.target.value ? parseInt(e.target.value) : undefined }))}
                  placeholder="무제한"
                  min="0"
                />
              </div>

              <div>
                <Label htmlFor="discount">할인율 (%)</Label>
                <Input
                  id="discount"
                  type="number"
                  value={formData.discount || ''}
                  onChange={(e: any) => setFormData((prev: Partial<ShopItem>) => ({ ...prev, discount: e.target.value ? parseInt(e.target.value) : undefined }))}
                  placeholder="0"
                  min="0"
                  max="100"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="category">카테고리 *</Label>
                <Select 
                  value={formData.category} 
                  onValueChange={(value: string) => setFormData((prev: Partial<ShopItem>) => ({ ...prev, category: value }))}        
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(category => (
                      <SelectItem key={category.value} value={category.value}>
                        {category.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="rarity">희귀도 *</Label>
                <Select 
                  value={formData.rarity} 
                  onValueChange={(value: string) => setFormData((prev: Partial<ShopItem>) => ({ ...prev, rarity: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {rarities.map(rarity => (
                      <SelectItem key={rarity.value} value={rarity.value}>
                        {rarity.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label htmlFor="tags">태그 (쉼표로 구분)</Label>
              <Input
                id="tags"
                value={Array.isArray(formData.tags) ? formData.tags.join(', ') : ''}
                onChange={(e: any) => setFormData((prev: Partial<ShopItem>) => ({ 
                  ...prev, 
                  tags: e.target.value.split(',').map((tag: string) => tag.trim()).filter(Boolean)
                }))}
                placeholder="태그1, 태그2, 태그3"
              />
            </div>

            <div className="flex items-center gap-3">
              <Switch
                checked={formData.isActive ?? true}
                onCheckedChange={(checked: boolean) => setFormData((prev: Partial<ShopItem>) => ({ ...prev, isActive: checked }))}
              />
              <Label>아이템 활성화</Label>
            </div>

            <div className="flex gap-3 pt-4 border-t border-border-secondary">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={isLoading}
                className="flex-1"
              >
                취소
              </Button>
              <Button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-gradient-game btn-hover-lift"
              >
                <Save className="w-4 h-4 mr-2" />
                {isLoading ? '저장 중...' : (editingItem ? '수정' : '생성')}
              </Button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}