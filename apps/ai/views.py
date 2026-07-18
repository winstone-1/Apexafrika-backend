from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from .models import AIConversation, AIMessage, AIPrediction
from .serializers import AIConversationSerializer, AIMessageSerializer, AIPredictionSerializer
import groq
import json

class AIConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AIConversationSerializer
    
    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        """Send a message to the AI (Groq)"""
        conversation = self.get_object()
        message = request.data.get('message')
        
        if not message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save user message
        user_message = AIMessage.objects.create(
            conversation=conversation,
            role='USER',
            content=message
        )
        
        # Get conversation history
        history = conversation.messages.all().order_by('created_at')
        messages = []
        for msg in history:
            messages.append({
                'role': msg.role.lower(),
                'content': msg.content
            })
        
        # Get AI response from Groq
        try:
            client = groq.Groq(api_key=settings.GROQ_API_KEY)
            
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=False
            )
            
            ai_response = response.choices[0].message.content
            
            # Save AI response
            assistant_message = AIMessage.objects.create(
                conversation=conversation,
                role='ASSISTANT',
                content=ai_response,
                metadata={
                    'model': 'llama3-70b-8192',
                    'tokens': response.usage.total_tokens
                }
            )
            
            return Response({
                'message': assistant_message.content,
                'conversation_id': conversation.id
            })
            
        except Exception as e:
            return Response(
                {'error': f'AI service error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def predict(self, request):
        """Make AI predictions"""
        prediction_type = request.data.get('type')
        match_id = request.data.get('match_id')
        tournament_id = request.data.get('tournament_id')
        
        # Build prediction context
        context = {}
        
        if match_id:
            from apps.tournaments.models import Match
            match = Match.objects.get(id=match_id)
            context['match'] = {
                'player1': match.player1.gamer_tag if match.player1 else 'TBD',
                'player2': match.player2.gamer_tag if match.player2 else 'TBD',
                'tournament': match.tournament.name,
                'round': match.round_number
            }
        
        try:
            client = groq.Groq(api_key=settings.GROQ_API_KEY)
            
            prompt = f"""
            Predict the outcome for this esports scenario:
            Type: {prediction_type}
            Context: {json.dumps(context)}
            
            Provide: winner prediction, confidence score (0-100), and reasoning.
            Format as JSON.
            """
            
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {'role': 'system', 'content': 'You are a professional esports analyst. Predict match and tournament outcomes.'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3,
                max_tokens=512
            )
            
            prediction = json.loads(response.choices[0].message.content)
            
            # Save prediction
            ai_prediction = AIPrediction.objects.create(
                type=prediction_type,
                match_id=match_id,
                tournament_id=tournament_id,
                prediction=prediction,
                confidence=prediction.get('confidence', 0.0)
            )
            
            return Response(AIPredictionSerializer(ai_prediction).data)
            
        except Exception as e:
            return Response(
                {'error': f'Prediction error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AIPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = AIPredictionSerializer
    queryset = AIPrediction.objects.all()
    filterset_fields = ['type', 'tournament', 'match']
