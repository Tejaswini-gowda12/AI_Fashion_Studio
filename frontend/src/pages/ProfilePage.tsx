import React, { useState } from 'react';
import { User as UserIcon, Mail, Shield, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';

export const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  const materialsList = [
    'Organic Cotton', 'Recycled Cotton', 'Hemp', 'Linen',
    'Tencel/Lyocell', 'Bamboo Lyocell', 'Econyl/recycled nylon',
    'Deadstock Fabric', 'Peace Silk', 'Organic Wool'
  ];

  const [selectedMaterials, setSelectedMaterials] = useState<string[]>(
    user?.preferred_materials || ['Organic Cotton', 'Hemp', 'Tencel/Lyocell']
  );

  const toggleMaterial = (mat: string) => {
    if (selectedMaterials.includes(mat)) {
      setSelectedMaterials(selectedMaterials.filter(m => m !== mat));
    } else {
      setSelectedMaterials([...selectedMaterials, mat]);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(false);
    try {
      await updateUser({
        full_name: fullName,
        preferred_materials: selectedMaterials
      });
      setSuccess(true);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-forest-900 dark:text-cream-100">User Profile & Eco Preferences</h1>
        <p className="text-xs text-sage-600 dark:text-sage-400">Manage account credentials and preferred fiber catalog filters.</p>
      </div>

      {success && (
        <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 text-emerald-800 dark:text-emerald-300 text-xs font-semibold flex items-center gap-2">
          <Check className="w-4 h-4 text-emerald-600" /> Profile updated successfully!
        </div>
      )}

      <Card className="space-y-6">
        <form onSubmit={handleSave} className="space-y-6">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-full bg-forest-900 text-cream-100 flex items-center justify-center font-bold text-2xl">
              {user?.full_name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h3 className="font-bold text-lg text-forest-900 dark:text-cream-100">{user?.full_name}</h3>
              <div className="flex items-center space-x-2 mt-1">
                <Badge variant={user?.role === 'admin' ? 'terracotta' : 'sage'}>
                  {user?.role.toUpperCase()}
                </Badge>
                <span className="text-xs text-sage-500">{user?.email}</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-cream-200 dark:border-charcoal-700">
            <div>
              <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-50 dark:bg-charcoal-900 text-xs focus:outline-none focus:ring-2 focus:ring-forest-900"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-charcoal-800 dark:text-cream-100 mb-1">Email Address</label>
              <input
                type="email"
                disabled
                value={user?.email || ''}
                className="w-full px-3 py-2 rounded-xl border border-cream-300 dark:border-charcoal-700 bg-cream-100 dark:bg-charcoal-800 text-xs opacity-70 cursor-not-allowed"
              />
            </div>
          </div>

          <div className="pt-4 border-t border-cream-200 dark:border-charcoal-700">
            <h4 className="font-bold text-sm text-forest-900 dark:text-cream-100 mb-2">Preferred Sustainable Materials Checklist</h4>
            <p className="text-xs text-sage-600 dark:text-sage-400 mb-3">Selected materials receive bonus weighting during AI fabric matching.</p>
            <div className="flex flex-wrap gap-2">
              {materialsList.map((mat) => {
                const isSelected = selectedMaterials.includes(mat);
                return (
                  <button
                    key={mat}
                    type="button"
                    onClick={() => toggleMaterial(mat)}
                    className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all border ${
                      isSelected
                        ? 'bg-forest-900 text-cream-100 border-forest-800 shadow-sm'
                        : 'bg-cream-100 dark:bg-charcoal-800 text-sage-700 dark:text-sage-400 border-cream-300 dark:border-charcoal-700 hover:border-forest-900'
                    }`}
                  >
                    {isSelected && <Check className="w-3.5 h-3.5 inline mr-1 text-emerald-400" />}
                    {mat}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="pt-4 flex justify-end">
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Profile Preferences'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};
