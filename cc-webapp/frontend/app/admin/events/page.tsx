"use client";
import React, { useEffect, useState, useCallback } from 'react';
import type { ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Plus, 
  Edit2, 
  Trash2, 
  Clock, 
  Gift, 
  CheckCircle,
  XCircle,
  AlertTriangle,
  Save,
  X,
  RefreshCw,
  Calendar,
} from 'lucide-react';
import { api } from '@/lib/unifiedApi';

interface AdminEvent {
  id: number;
  name: string;
  start_at: string;
  end_at: string;
  reward_scheme: any;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface EventFormData {
  name: string;
  start_at: string;
  end_at: string;
  reward_scheme: any;
}

export default function AdminEventsPage() {
  const router = useRouter();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    start_at: '',
    end_at: '',
    reward_scheme: { gold: 1000, experience: 100 },
  });

  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('admin/content/events') as AdminEvent[];
      setEvents(response);
    } catch (err: any) {
      setError(err.message || '이벤트 로드 실패');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const handleCreate = async () => {
    try {
      await api.post('admin/content/events', formData);
      setShowCreateForm(false);
      setFormData({ name: '', start_at: '', end_at: '', reward_scheme: { gold: 1000, experience: 100 } });
      await loadEvents();
    } catch (err: any) {
      setError(err.message || '이벤트 생성 실패');
    }
  };

  const handleUpdate = async () => {
    if (!editingEvent) return;
    try {
      await api.put(`admin/content/events/${editingEvent.id}`, formData);
      setEditingEvent(null);
      setFormData({ name: '', start_at: '', end_at: '', reward_scheme: { gold: 1000, experience: 100 } });
      await loadEvents();
    } catch (err: any) {
      setError(err.message || '이벤트 수정 실패');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    try {
      await api.del(`admin/content/events/${id}`);
      await loadEvents();
    } catch (err: any) {
      setError(err.message || '이벤트 삭제 실패');
    }
  };

  const handleToggleActive = async (id: number, isActive: boolean) => {
    try {
      if (isActive) {
        await api.post(`admin/content/events/${id}/deactivate`);
      } else {
        await api.post(`admin/content/events/${id}/activate`);
      }
      await loadEvents();
    } catch (err: any) {
      setError(err.message || '상태 변경 실패');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  const getEventStatus = (event: AdminEvent) => {
    const now = new Date();
    const start = new Date(event.start_at);
    const end = new Date(event.end_at);
    
    if (!event.is_active) return { status: 'inactive', label: '비활성', color: 'text-gray-400' };
    if (now < start) return { status: 'scheduled', label: '예정', color: 'text-blue-400' };
    if (now > end) return { status: 'ended', label: '종료', color: 'text-gray-400' };
    return { status: 'active', label: '진행중', color: 'text-green-400' };
  };

  const startEdit = (event: AdminEvent) => {
    setEditingEvent(event);
    setFormData({
      name: event.name,
      start_at: event.start_at.slice(0, 16), // YYYY-MM-DDTHH:MM
      end_at: event.end_at.slice(0, 16),
      reward_scheme: event.reward_scheme,
    });
  };

  const cancelEdit = () => {
    setEditingEvent(null);
    setShowCreateForm(false);
    setFormData({ name: '', start_at: '', end_at: '', reward_scheme: { gold: 1000, experience: 100 } });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-neutral-950 to-black text-gray-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <button 
              onClick={() => router.push('/admin')} 
              className="p-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                이벤트 관리
              </h1>
              <p className="text-sm text-gray-400 mt-1">이벤트 생성, 수정, 활성화 관리</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button 
              onClick={loadEvents} 
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-sm transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>새로고침</span>
            </button>
            <button 
              onClick={() => setShowCreateForm(true)} 
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 text-sm transition-all"
            >
              <Plus className="h-4 w-4" />
              <span>새 이벤트</span>
            </button>
          </div>
        </header>

        {/* 에러 메시지 */}
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-lg bg-red-950/50 border border-red-800"
          >
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-400" />
              <span className="text-red-400">{error}</span>
            </div>
          </motion.div>
        )}

        {/* 이벤트 생성/수정 폼 */}
        {(showCreateForm || editingEvent) && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 p-6 rounded-xl bg-neutral-900 border border-neutral-800"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">
                {editingEvent ? '이벤트 수정' : '새 이벤트 생성'}
              </h2>
              <button onClick={cancelEdit} className="p-2 rounded-lg hover:bg-neutral-800 transition-colors">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">이벤트 이름</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e: any) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-neutral-800 border border-neutral-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="이벤트 이름을 입력하세요"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">보상 구성</label>
                <textarea
                  value={JSON.stringify(formData.reward_scheme, null, 2)}
                  onChange={(e: any) => {
                    try {
                      setFormData({ ...formData, reward_scheme: JSON.parse(e.target.value) });
                    } catch {
                      // JSON 파싱 오류 시 무시
                    }
                  }}
                  className="w-full px-3 py-2 rounded-lg bg-neutral-800 border border-neutral-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={4}
                  placeholder='{"gold": 1000, "experience": 100}'
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">시작 시간</label>
                <input
                  type="datetime-local"
                  value={formData.start_at}
                  onChange={(e: any) => setFormData({ ...formData, start_at: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-neutral-800 border border-neutral-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">종료 시간</label>
                <input
                  type="datetime-local"
                  value={formData.end_at}
                  onChange={(e: any) => setFormData({ ...formData, end_at: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-neutral-800 border border-neutral-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={cancelEdit}
                className="px-4 py-2 rounded-lg bg-neutral-700 hover:bg-neutral-600 transition-colors"
              >
                취소
              </button>
              <button
                onClick={editingEvent ? handleUpdate : handleCreate}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 transition-all"
              >
                <Save className="h-4 w-4" />
                <span>{editingEvent ? '수정' : '생성'}</span>
              </button>
            </div>
          </motion.div>
        )}

        {/* 이벤트 목록 */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-purple-400" />
              <p className="text-gray-400">이벤트를 로드하는 중...</p>
            </div>
          ) : events.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-400">등록된 이벤트가 없습니다.</p>
            </div>
          ) : (
            events.map((event: any) => {
              const status = getEventStatus(event);
              return (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-6 rounded-xl bg-neutral-900 border border-neutral-800 hover:border-neutral-700 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-white">{event.name}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color} bg-neutral-800`}>
                          {status.label}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-400">
                        <div className="flex items-center space-x-2">
                          <Clock className="h-4 w-4" />
                          <span>시작: {formatDate(event.start_at)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Clock className="h-4 w-4" />
                          <span>종료: {formatDate(event.end_at)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Gift className="h-4 w-4" />
                          <span>보상: {JSON.stringify(event.reward_scheme)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Calendar className="h-4 w-4" />
                          <span>생성: {formatDate(event.created_at)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleToggleActive(event.id, event.is_active)}
                        className={`p-2 rounded-lg transition-colors ${
                          event.is_active 
                            ? 'bg-green-600 hover:bg-green-700' 
                            : 'bg-gray-600 hover:bg-gray-700'
                        }`}
                        title={event.is_active ? '비활성화' : '활성화'}
                      >
                        {event.is_active ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                      </button>
                      
                      <button
                        onClick={() => startEdit(event)}
                        className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 transition-colors"
                        title="수정"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      
                      <button
                        onClick={() => handleDelete(event.id)}
                        className="p-2 rounded-lg bg-red-600 hover:bg-red-700 transition-colors"
                        title="삭제"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
