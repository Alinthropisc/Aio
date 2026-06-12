import 'package:equatable/equatable.dart';

class User extends Equatable {
  final String id;
  final String email;
  final String? fullName;
  final bool isActive;

  const User({
    required this.id,
    required this.email,
    this.fullName,
    this.isActive = true,
  });

  @override
  List<Object?> get props => [id, email, fullName, isActive];
}
