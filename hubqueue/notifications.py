"""
Notifications module for HubQueue.
"""
import os
import json
import time
from datetime import datetime, timedelta
from github import Github
from github.GithubException import GithubException
from .auth import get_github_token
from .logging import get_logger

# Get logger
logger = get_logger()


def list_notifications(all=False, participating=False, since=None, before=None, token=None):
    """
    List notifications for the authenticated user.
    
    Args:
        all (bool, optional): If True, show all notifications, including ones marked as read.
        participating (bool, optional): If True, only show notifications in which the user is
            directly participating or mentioned.
        since (str, optional): Only show notifications updated after the given time.
            This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        before (str, optional): Only show notifications updated before the given time.
            This is a timestamp in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        list: List of notification dictionaries or None if listing failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug("Listing notifications")
        github = Github(token)
        
        # Get notifications
        notifications = []
        for notification in github.get_user().get_notifications(all=all, participating=participating, since=since, before=before):
            # Get subject details
            subject_type = notification.subject.type
            subject_title = notification.subject.title
            subject_url = notification.subject.url
            subject_latest_comment_url = notification.subject.latest_comment_url
            
            # Get repository details
            repo_name = notification.repository.full_name
            repo_url = notification.repository.html_url
            
            # Get notification details
            notification_id = notification.id
            notification_unread = notification.unread
            notification_reason = notification.reason
            notification_updated_at = notification.updated_at
            
            notifications.append({
                "id": notification_id,
                "unread": notification_unread,
                "reason": notification_reason,
                "updated_at": notification_updated_at,
                "subject": {
                    "type": subject_type,
                    "title": subject_title,
                    "url": subject_url,
                    "latest_comment_url": subject_latest_comment_url,
                },
                "repository": {
                    "name": repo_name,
                    "url": repo_url,
                },
            })
        
        logger.info(f"Found {len(notifications)} notifications")
        return notifications
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error listing notifications: {str(e)}")
        raise Exception(f"Error listing notifications: {str(e)}")


def mark_notification_as_read(notification_id, token=None):
    """
    Mark a notification as read.
    
    Args:
        notification_id (str): Notification ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if marking as read was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Marking notification as read: {notification_id}")
        github = Github(token)
        
        # Get notifications
        for notification in github.get_user().get_notifications():
            if notification.id == notification_id:
                notification.mark_as_read()
                logger.info(f"Marked notification as read: {notification_id}")
                return True
        
        logger.error(f"Notification not found: {notification_id}")
        return False
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise Exception(f"Error marking notification as read: {str(e)}")


def mark_all_notifications_as_read(repo_name=None, token=None):
    """
    Mark all notifications as read.
    
    Args:
        repo_name (str, optional): Repository name in format 'owner/repo'.
            If provided, only mark notifications for this repository as read.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        bool: True if marking as read was successful, False otherwise
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return False
    
    try:
        logger.debug(f"Marking all notifications as read{f' for {repo_name}' if repo_name else ''}")
        github = Github(token)
        
        if repo_name:
            # Mark notifications for repository as read
            repo = github.get_repo(repo_name)
            github.get_user().mark_notifications_as_read(repo=repo)
            logger.info(f"Marked all notifications as read for {repo_name}")
        else:
            # Mark all notifications as read
            github.get_user().mark_notifications_as_read()
            logger.info("Marked all notifications as read")
        
        return True
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error marking notifications as read: {str(e)}")
        raise Exception(f"Error marking notifications as read: {str(e)}")


def get_notification_details(notification_id, token=None):
    """
    Get detailed information about a notification.
    
    Args:
        notification_id (str): Notification ID
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Notification details or None if retrieval failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Getting notification details: {notification_id}")
        github = Github(token)
        
        # Get notifications
        for notification in github.get_user().get_notifications(all=True):
            if notification.id == notification_id:
                # Get subject details
                subject_type = notification.subject.type
                subject_title = notification.subject.title
                subject_url = notification.subject.url
                subject_latest_comment_url = notification.subject.latest_comment_url
                
                # Get repository details
                repo_name = notification.repository.full_name
                repo_url = notification.repository.html_url
                
                # Get notification details
                notification_unread = notification.unread
                notification_reason = notification.reason
                notification_updated_at = notification.updated_at
                
                # Get thread subscription
                try:
                    subscription = notification.get_thread_subscription()
                    subscription_subscribed = subscription.subscribed
                    subscription_ignored = subscription.ignored
                    subscription_reason = subscription.reason
                except Exception:
                    subscription_subscribed = None
                    subscription_ignored = None
                    subscription_reason = None
                
                # Get subject content
                subject_content = None
                if subject_type == "Issue":
                    # Get issue
                    issue_number = int(subject_url.split("/")[-1])
                    issue = notification.repository.get_issue(issue_number)
                    subject_content = {
                        "number": issue.number,
                        "state": issue.state,
                        "title": issue.title,
                        "body": issue.body,
                        "created_at": issue.created_at,
                        "updated_at": issue.updated_at,
                        "closed_at": issue.closed_at,
                        "user": {
                            "login": issue.user.login,
                            "url": issue.user.html_url,
                        },
                        "labels": [label.name for label in issue.labels],
                        "comments": issue.comments,
                    }
                elif subject_type == "PullRequest":
                    # Get pull request
                    pr_number = int(subject_url.split("/")[-1])
                    pr = notification.repository.get_pull(pr_number)
                    subject_content = {
                        "number": pr.number,
                        "state": pr.state,
                        "title": pr.title,
                        "body": pr.body,
                        "created_at": pr.created_at,
                        "updated_at": pr.updated_at,
                        "closed_at": pr.closed_at,
                        "merged_at": pr.merged_at,
                        "user": {
                            "login": pr.user.login,
                            "url": pr.user.html_url,
                        },
                        "labels": [label.name for label in pr.labels],
                        "comments": pr.comments,
                        "additions": pr.additions,
                        "deletions": pr.deletions,
                        "changed_files": pr.changed_files,
                    }
                elif subject_type == "Release":
                    # Get release
                    release_id = int(subject_url.split("/")[-1])
                    release = notification.repository.get_release(release_id)
                    subject_content = {
                        "id": release.id,
                        "tag_name": release.tag_name,
                        "name": release.title,
                        "body": release.body,
                        "created_at": release.created_at,
                        "published_at": release.published_at,
                        "draft": release.draft,
                        "prerelease": release.prerelease,
                        "author": {
                            "login": release.author.login,
                            "url": release.author.html_url,
                        },
                    }
                
                logger.info(f"Retrieved notification details: {notification_id}")
                return {
                    "id": notification_id,
                    "unread": notification_unread,
                    "reason": notification_reason,
                    "updated_at": notification_updated_at,
                    "subject": {
                        "type": subject_type,
                        "title": subject_title,
                        "url": subject_url,
                        "latest_comment_url": subject_latest_comment_url,
                        "content": subject_content,
                    },
                    "repository": {
                        "name": repo_name,
                        "url": repo_url,
                    },
                    "subscription": {
                        "subscribed": subscription_subscribed,
                        "ignored": subscription_ignored,
                        "reason": subscription_reason,
                    },
                }
        
        logger.error(f"Notification not found: {notification_id}")
        return None
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error getting notification details: {str(e)}")
        raise Exception(f"Error getting notification details: {str(e)}")


def subscribe_to_thread(notification_id, subscribed=True, ignored=False, token=None):
    """
    Subscribe to a notification thread.
    
    Args:
        notification_id (str): Notification ID
        subscribed (bool, optional): If True, subscribe to the thread. Defaults to True.
        ignored (bool, optional): If True, ignore the thread. Defaults to False.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        dict: Subscription details or None if subscription failed
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return None
    
    try:
        logger.debug(f"Subscribing to thread: {notification_id}")
        github = Github(token)
        
        # Get notifications
        for notification in github.get_user().get_notifications(all=True):
            if notification.id == notification_id:
                # Subscribe to thread
                subscription = notification.set_thread_subscription(subscribed, ignored)
                
                logger.info(f"Subscribed to thread: {notification_id}")
                return {
                    "subscribed": subscription.subscribed,
                    "ignored": subscription.ignored,
                    "reason": subscription.reason,
                    "created_at": subscription.created_at,
                    "url": subscription.url,
                }
        
        logger.error(f"Notification not found: {notification_id}")
        return None
    except GithubException as e:
        error_message = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
        logger.error(f"GitHub API error: {error_message}")
        raise Exception(f"GitHub API error: {error_message}")
    except Exception as e:
        logger.error(f"Error subscribing to thread: {str(e)}")
        raise Exception(f"Error subscribing to thread: {str(e)}")


def poll_notifications(interval=60, callback=None, token=None):
    """
    Poll for new notifications.
    
    Args:
        interval (int, optional): Polling interval in seconds. Defaults to 60.
        callback (callable, optional): Callback function to call when new notifications are found.
            The function should accept a list of notification dictionaries as its only argument.
        token (str, optional): GitHub token. If None, will try to get from config.
        
    Returns:
        None
    """
    token = token or get_github_token()
    if not token:
        logger.error("GitHub token not provided")
        return
    
    try:
        logger.debug(f"Polling for notifications (interval: {interval}s)")
        
        # Get initial notifications
        last_check = datetime.utcnow()
        known_notifications = set()
        
        # Get current notifications
        notifications = list_notifications(token=token)
        for notification in notifications:
            known_notifications.add(notification["id"])
        
        logger.info(f"Initial notifications: {len(known_notifications)}")
        
        # Poll for new notifications
        while True:
            # Sleep for interval
            time.sleep(interval)
            
            # Get new notifications
            since = last_check.strftime("%Y-%m-%dT%H:%M:%SZ")
            last_check = datetime.utcnow()
            
            try:
                # Get notifications
                notifications = list_notifications(since=since, token=token)
                
                # Check for new notifications
                new_notifications = []
                for notification in notifications:
                    if notification["id"] not in known_notifications:
                        new_notifications.append(notification)
                        known_notifications.add(notification["id"])
                
                # Call callback if new notifications found
                if new_notifications and callback:
                    logger.info(f"Found {len(new_notifications)} new notifications")
                    callback(new_notifications)
            except Exception as e:
                logger.error(f"Error polling for notifications: {str(e)}")
    except KeyboardInterrupt:
        logger.info("Polling stopped")
    except Exception as e:
        logger.error(f"Error polling for notifications: {str(e)}")
        raise Exception(f"Error polling for notifications: {str(e)}")
