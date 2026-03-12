// Vote management

let currentUser = null;
let hasVotedInEvent = {};

function initVoting(user) {
  currentUser = user;
}

async function checkVoteStatus(eventId) {
  if (!currentUser) return;
  try {
    const data = await apiCall(`../cgi-bin/check_voted.py?voter_user_id=${currentUser.user_id}&event_id=${eventId}`);
    if (data.status === 'success') {
      hasVotedInEvent[eventId] = data.has_voted;
      if (data.has_voted && data.participant_id) {
        markAsVoted(data.participant_id, eventId);
      }
    }
  } catch (e) {}
}

function markAsVoted(votedParticipantId, eventId) {
  // Disable all vote buttons for this event
  document.querySelectorAll(`.vote-btn[data-event="${eventId}"]`).forEach(btn => {
    btn.disabled = true;
    btn.classList.remove('btn-primary', 'btn-outline-primary');
    btn.classList.add('btn-secondary');
    btn.innerHTML = '<i class="bi bi-lock-fill me-1"></i>Voted';
  });

  // Mark the voted participant's button
  const votedBtn = document.querySelector(`.vote-btn[data-participant="${votedParticipantId}"]`);
  if (votedBtn) {
    votedBtn.classList.remove('btn-secondary');
    votedBtn.classList.add('btn-success');
    votedBtn.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>Your Vote';
  }
}

async function castVote(participantId, eventId) {
  if (!currentUser) {
    showToast('Please log in to vote', 'warning');
    return;
  }

  if (hasVotedInEvent[eventId]) {
    showToast('You have already voted in this event!', 'warning');
    return;
  }

  const btn = document.getElementById(`btn-${participantId}`);
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Voting...';
  }

  try {
    const data = await apiCall('../cgi-bin/cast_vote.py', 'POST', {
      voter_user_id: currentUser.user_id,
      participant_id: participantId,
      event_id: eventId
    });

    if (data.status === 'success') {
      // Update vote count
      const voteCountEl = document.getElementById(`votes-${participantId}`);
      if (voteCountEl) voteCountEl.textContent = data.new_vote_count;

      hasVotedInEvent[eventId] = true;
      markAsVoted(participantId, eventId);
      showToast('🎉 Your vote has been cast successfully!', 'success');

      // Fire small confetti
      if (typeof confetti !== 'undefined') {
        confetti({ particleCount: 50, spread: 70, origin: { y: 0.6 }, colors: ['#7B2FBE', '#FFB400'] });
      }
    } else {
      showToast(data.message || 'Failed to cast vote', 'danger');
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-hand-thumbs-up me-1"></i>Vote';
      }
    }
  } catch (e) {
    showToast('Network error. Please try again.', 'danger');
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-hand-thumbs-up me-1"></i>Vote';
    }
  }
}
