<template>
    <div class="layout-wrapper">
        <div class="layout-content">
            <div class="profile-container">
                <div class="profile-header bg-primary text-white py-6 px-8 rounded-lg shadow-md mb-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <h1 class="text-3xl font-bold">{{ user.username }}</h1>
                        </div>
                        <div class="text-right">
                            <p class="text-lg font-semibold">Experience Level</p>
                            <p class="text-xl">{{ user.experience_level }}</p>
                        </div>
                    </div>
                </div>

                <!-- Profile Info Section -->
                <div class="bg-surface-0 dark:bg-surface-800 p-6 rounded-lg shadow">
                    <h2 class="text-xl font-semibold mb-4">Profile Information</h2>
                    <div class="space-y-6">
                        <div>
                            <label class="block text-sm text-muted-color mb-1">Description</label>
                            <p class="text-surface-900 dark:text-surface-0">{{ user.description || 'No description yet'
                                }}</p>
                        </div>
                        <div>
                            <label class="block text-sm text-muted-color mb-1">Member Since</label>
                            <p class="text-surface-900 dark:text-surface-0">{{ formatDate(user.date_joined) }}</p>
                        </div>
                        <div>
                            <label class="block text-sm text-muted-color mb-1">Password Last Changed</label>
                            <p class="text-surface-900 dark:text-surface-0">{{ formatDate(user.password_last_changed) }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="mt-6 text-right space-x-2">
                    <Button label="Change Password" icon="pi pi-lock" @click="showPasswordDialog"
                        class="p-button-secondary" />
                    <Button label="Edit Profile" icon="pi pi-pencil" @click="showEditDialog" />
                </div>

                <!-- Edit Profile Dialog -->
                <Dialog v-model:visible="editDialogVisible" header="Edit Profile" :modal="true"
                    class="edit-profile-dialog" :contentClass="'surface-ground'" :headerClass="'surface-section'">
                    <div class="surface-section p-4 rounded-lg">
                        <div class="field mb-4">
                            <label for="experience_level"
                                class="block text-surface-900 dark:text-surface-0 text-sm font-medium mb-2">Experience
                                Level</label>
                            <Dropdown v-model="editForm.experience_level" :options="experienceLevels"
                                optionLabel="label" optionValue="value" placeholder="Select Experience Level"
                                class="w-full" />
                        </div>
                        <div class="field mb-4">
                            <label for="description"
                                class="block text-surface-900 dark:text-surface-0 text-sm font-medium mb-2">Description</label>
                            <Textarea v-model="editForm.description" rows="4" class="w-full"
                                placeholder="Tell us about yourself..." />
                        </div>
                    </div>
                    <template #footer>
                        <div class="surface-section py-3 px-6 flex justify-end gap-2">
                            <Button label="Cancel" icon="pi pi-times" @click="hideEditDialog" class="p-button-text" />
                            <Button label="Save" icon="pi pi-check" @click="saveProfile" autofocus />
                        </div>
                    </template>
                </Dialog>

                <!-- Change Password Dialog -->
                <Dialog v-model:visible="passwordDialogVisible" header="Change Password" :modal="true"
                    class="edit-profile-dialog" :contentClass="'surface-ground'" :headerClass="'surface-section'">
                    <div class="surface-section p-4 rounded-lg">
                        <div class="field mb-4">
                            <label for="current_password"
                                class="block text-surface-900 dark:text-surface-0 text-sm font-medium mb-2">Current
                                Password</label>
                            <Password v-model="passwordForm.current_password" :feedback="false" toggleMask
                                class="w-full" inputClass="w-full" />
                        </div>
                        <div class="field mb-4">
                            <label for="new_password"
                                class="block text-surface-900 dark:text-surface-0 text-sm font-medium mb-2">New
                                Password</label>
                            <Password v-model="passwordForm.new_password" toggleMask class="w-full"
                                inputClass="w-full" />
                        </div>
                        <div class="field mb-4">
                            <label for="confirm_password"
                                class="block text-surface-900 dark:text-surface-0 text-sm font-medium mb-2">Confirm New
                                Password</label>
                            <Password v-model="passwordForm.confirm_password" :feedback="false" toggleMask
                                class="w-full" inputClass="w-full" />
                        </div>
                        <small v-if="passwordError" class="p-error block mt-2">{{ passwordError }}</small>
                    </div>
                    <template #footer>
                        <div class="surface-section py-3 px-6 flex justify-end gap-2">
                            <Button label="Cancel" icon="pi pi-times" @click="hidePasswordDialog"
                                class="p-button-text" />
                            <Button label="Change Password" icon="pi pi-check" @click="changePassword" autofocus />
                        </div>
                    </template>
                </Dialog>
            </div>
        </div>
    </div>
</template>

<script>
import { useAuthStore } from '@/store/auth';
import { getCSRFToken } from '@/store/auth';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import Textarea from 'primevue/textarea';
import Password from 'primevue/password';

export default {
    components: {
        Button,
        Dialog,
        Dropdown,
        Textarea,
        Password
    },
    data() {
        return {
            user: {
                username: '',
                email: '',
                experience_level: '',
                description: '',
                password_last_changed: null,
                date_joined: null
            },
            editDialogVisible: false,
            passwordDialogVisible: false,
            editForm: {
                experience_level: '',
                description: ''
            },
            passwordForm: {
                current_password: '',
                new_password: '',
                confirm_password: ''
            },
            passwordError: '',
            experienceLevels: [
                { label: 'Beginner', value: 'beginner' },
                { label: 'Intermediate', value: 'intermediate' },
                { label: 'Advanced', value: 'advanced' }
            ]
        };
    },
    methods: {
        async fetchProfile() {
            try {
                const response = await fetch('http://localhost:8000/api/profile', {
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    this.user = data;
                }
            } catch (error) {
                console.error('Failed to fetch profile', error);
            }
        },
        formatDate(date) {
            if (!date) return 'Not available';
            return new Date(date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        },
        showEditDialog() {
            this.editForm = {
                experience_level: this.user.experience_level,
                description: this.user.description
            };
            this.editDialogVisible = true;
        },
        hideEditDialog() {
            this.editDialogVisible = false;
        },
        showPasswordDialog() {
            this.passwordForm = {
                current_password: '',
                new_password: '',
                confirm_password: ''
            };
            this.passwordError = '';
            this.passwordDialogVisible = true;
        },
        hidePasswordDialog() {
            this.passwordDialogVisible = false;
            this.passwordError = '';
        },
        async changePassword() {
            this.passwordError = '';

            if (this.passwordForm.new_password !== this.passwordForm.confirm_password) {
                this.passwordError = 'New passwords do not match';
                return;
            }

            if (this.passwordForm.new_password.length < 8) {
                this.passwordError = 'Password must be at least 8 characters long';
                return;
            }

            try {
                const response = await fetch('http://localhost:8000/api/profile/change-password', {
                    method: 'PUT',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        current_password: this.passwordForm.current_password,
                        new_password: this.passwordForm.new_password
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    this.hidePasswordDialog();
                    // Refresh profile to get updated password_last_changed
                    await this.fetchProfile();
                } else {
                    this.passwordError = data.message || 'Failed to change password';
                }
            } catch (error) {
                console.error('Error changing password:', error);
                this.passwordError = 'An error occurred while changing password';
            }
        },
        async saveProfile() {
            try {
                const response = await fetch('http://localhost:8000/api/profile/update', {
                    method: 'PUT',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify(this.editForm)
                });

                if (response.ok) {
                    const data = await response.json();
                    this.user.experience_level = data.experience_level;
                    this.user.description = data.description;
                    this.hideEditDialog();
                } else {
                    const error = await response.json();
                    console.error('Failed to update profile:', error.message);
                }
            } catch (error) {
                console.error('Error updating profile:', error);
            }
        }
    },
    async mounted() {
        await this.fetchProfile();
    }
};
</script>

<style scoped>
.profile-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

.text-muted-color {
    color: var(--text-color-secondary);
}

:deep(.edit-profile-dialog) {
    max-width: 90vw;
    width: 500px;
}

:deep(.edit-profile-dialog .p-dialog-header) {
    padding: 1.5rem;
}

:deep(.edit-profile-dialog .p-dialog-content) {
    padding: 0;
}

:deep(.p-dropdown),
:deep(.p-inputtextarea),
:deep(.p-password) {
    width: 100%;
}

:deep(.p-password-input) {
    width: 100%;
}
</style>
