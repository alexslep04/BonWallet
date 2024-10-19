from server.rewards import rewards_bp
from flask import Blueprint, jsonify, abort, request
from server.config import db
from server.rewards.models import CardRewards, PointRewards, QualifyingService, QualifyingLocation
from server.restaurant_scraper  import get_merchants_data, extract_single_reward_data  # Assuming your scraper file is named scraper.py

# Getter for CardRewards by id
@rewards_bp.route('/card_rewards/<int:id>', methods=['GET'])
def get_card_rewards(id):
    card = CardRewards.query.get(id)
    if not card:
        return abort(404, description="CardRewards not found")
    
    return jsonify({
        'id': card.id,
        'card_name': card.card_name,
        'point_rewards': [pr.id for pr in card.point_rewards],  # Assuming you just want the IDs
        'additional_benefits': card.additional_benefits,
        'offer_terms_url': card.offer_terms_url,
        'benefit_terms_url': card.benefit_terms_url
    })

# Getter for PointRewards by id
@rewards_bp.route('/point_rewards/<int:id>', methods=['GET'])
def get_point_rewards(id):
    point = PointRewards.query.get(id)
    if not point:
        return abort(404, description="PointRewards not found")
    
    return jsonify({
        'id': point.id,
        'multiplier': point.multiplier,
        'qualifying': [q.id for q in point.qualifying]  # Assuming you just want the IDs
    })


@rewards_bp.route('/qualifying/<int:id>', methods=['GET'])
def get_qualifying(id):
    qualifying = Qualifying.query.get(id)
    if not qualifying:
        return abort(404, description="Qualifying not found")
    
    response = {
        'id': qualifying.id,
        'name': qualifying.name,
        'type': qualifying.type  # This will be either 'service' or 'location'
    }

    # If it's a service, include service_type
    if qualifying.type == 'service':
        response['service_type'] = qualifying.service_type
    
    # If it's a location, include location_type
    elif qualifying.type == 'location':
        response['location_type'] = qualifying.location_type
    
    return jsonify(response)


# Endpoint to check if a user is at a qualifying location
@rewards_bp.route('/check_rewards', methods=['POST'])
def check_rewards():
    try:
        # Extract location data from the incoming JSON request
        user_data = request.get_json()
        user_location = user_data.get('location')

        if not user_location:
            return jsonify({"error": "Location data is missing"}), 400

        # Use the existing functions to get and extract reward data
        data = get_merchants_data(API_URL, user_location)
        merchants = data.get("merchants", [])
        reward_data = extract_single_reward_data(merchants)

        if reward_data:
            return jsonify(reward_data), 200
        else:
            return jsonify({}), 200  # Empty JSON response if no location matches the criteria

    except Exception as e:
        return jsonify({"error": str(e)}), 500
