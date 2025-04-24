<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
    notifications: {
        type: Array,
        default: () => []
    }
});

const groupNotificationsByDate = (notifications) => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    const lastWeek = new Date(today);
    lastWeek.setDate(lastWeek.getDate() - 7);

    return {
        today: notifications.filter(n => {
            const notifDate = new Date(n.date);
            return notifDate.toDateString() === today.toDateString();
        }),
        yesterday: notifications.filter(n => {
            const notifDate = new Date(n.date);
            return notifDate.toDateString() === yesterday.toDateString();
        }),
        lastWeek: notifications.filter(n => {
            const notifDate = new Date(n.date);
            return notifDate < yesterday && notifDate >= lastWeek;
        })
    };
};

const groupedNotifications = computed(() => groupNotificationsByDate(props.notifications));
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-6">
            <div class="font-semibold text-xl">Notifications</div>
        </div>

        <template v-if="groupedNotifications.today.length > 0">
            <span class="block text-muted-color font-medium mb-4">TODAY</span>
            <ul class="p-0 mx-0 mt-0 mb-6 list-none">
                <li v-for="notification in groupedNotifications.today" :key="notification.id" class="flex items-center py-2 border-b border-surface">
                    <div :class="`w-12 h-12 flex items-center justify-center bg-${notification.iconColor}-100 dark:bg-${notification.iconColor}-400/10 rounded-full mr-4 shrink-0`">
                        <i :class="`pi pi-${notification.icon} !text-xl text-${notification.iconColor}-500`"></i>
                    </div>
                    <span class="text-surface-900 dark:text-surface-0 leading-normal" v-html="notification.message"></span>
                </li>
            </ul>
        </template>

        <template v-if="groupedNotifications.yesterday.length > 0">
            <span class="block text-muted-color font-medium mb-4">YESTERDAY</span>
            <ul class="p-0 m-0 list-none mb-6">
                <li v-for="notification in groupedNotifications.yesterday" :key="notification.id" class="flex items-center py-2 border-b border-surface">
                    <div :class="`w-12 h-12 flex items-center justify-center bg-${notification.iconColor}-100 dark:bg-${notification.iconColor}-400/10 rounded-full mr-4 shrink-0`">
                        <i :class="`pi pi-${notification.icon} !text-xl text-${notification.iconColor}-500`"></i>
                    </div>
                    <span class="text-surface-900 dark:text-surface-0 leading-normal" v-html="notification.message"></span>
                </li>
            </ul>
        </template>

        <template v-if="groupedNotifications.lastWeek.length > 0">
            <span class="block text-muted-color font-medium mb-4">LAST WEEK</span>
            <ul class="p-0 m-0 list-none">
                <li v-for="notification in groupedNotifications.lastWeek" :key="notification.id" class="flex items-center py-2 border-b border-surface">
                    <div :class="`w-12 h-12 flex items-center justify-center bg-${notification.iconColor}-100 dark:bg-${notification.iconColor}-400/10 rounded-full mr-4 shrink-0`">
                        <i :class="`pi pi-${notification.icon} !text-xl text-${notification.iconColor}-500`"></i>
                    </div>
                    <span class="text-surface-900 dark:text-surface-0 leading-normal" v-html="notification.message"></span>
                </li>
            </ul>
        </template>

        <div v-if="notifications.length === 0" class="text-center py-4 text-muted-color">
            No notifications
        </div>
    </div>
</template>
